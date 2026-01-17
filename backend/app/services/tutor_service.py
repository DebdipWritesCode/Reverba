from datetime import datetime
from bson import ObjectId
from openai import OpenAI
from app.database import get_tutor_chats_collection, get_words_collection
from app.models.tutor_chat import TutorEvaluationRequest, TutorEvaluationResponse, ChatMessage, EvaluationResult
from app.models.daily_task import TaskType, TaskResult
from app.settings.get_env import OPENAI_API_KEY, OPENAI_MODEL
import json
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

async def evaluate_response(
    user_id: str,
    request: TutorEvaluationRequest
) -> dict:
    """Evaluate user response using AI tutor"""
    if not client:
        raise Exception("OpenAI API key not configured")
    
    words_collection = get_words_collection()
    tutor_chats_collection = get_tutor_chats_collection()
    
    # Get word information
    word = await words_collection.find_one({
        "_id": ObjectId(request.wordId),
        "userId": ObjectId(user_id)
    })
    
    if not word:
        raise Exception("Word not found")
    
    # Check for existing chat to get conversation history
    existing_chat = await tutor_chats_collection.find_one({
        "userId": ObjectId(user_id),
        "wordId": ObjectId(request.wordId),
        "taskType": request.taskType.value
    }, sort=[("createdAt", -1)])
    
    messages = []
    failure_count = 0
    
    if existing_chat:
        # Load existing conversation
        messages = existing_chat.get("messages", [])
        # Count failures in existing messages
        for msg in messages:
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                if "FAIL" in content or "incorrect" in content.lower() or "wrong" in content.lower():
                    failure_count += 1
    
    # Build system prompt based on task type
    system_prompt = _build_system_prompt(request.taskType, word)
    
    # Add user response
    messages.append({
        "role": "user",
        "content": request.userResponse
    })
    
    # Build evaluation prompt
    evaluation_prompt = _build_evaluation_prompt(
        word,
        request.taskType,
        request.userResponse,
        failure_count
    )
    
    try:
        # Call OpenAI
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": evaluation_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        evaluation = json.loads(content)
        
        result = evaluation.get("result", "FAIL")
        feedback = evaluation.get("feedback", "")
        hint = evaluation.get("hint")
        answer_revealed = evaluation.get("answerRevealed", False)
        
        # Add assistant response to messages
        assistant_message = {
            "role": "assistant",
            "content": feedback
        }
        if hint:
            assistant_message["content"] += f"\n\nHint: {hint}"
        if answer_revealed:
            assistant_message["content"] += f"\n\nCorrect answer: {word.get('meaning')}"
        
        messages.append(assistant_message)
        
        # Determine final result
        final_result = TaskResult.PASS if result == "PASS" else TaskResult.FAIL
        
        # Save or update chat
        if existing_chat:
            # Update existing chat
            await tutor_chats_collection.update_one(
                {"_id": existing_chat["_id"]},
                {
                    "$set": {
                        "messages": messages,
                        "finalResult": final_result.value
                    }
                }
            )
            chat_id = str(existing_chat["_id"])
        else:
            # Create new chat
            chat_doc = {
                "userId": ObjectId(user_id),
                "wordId": ObjectId(request.wordId),
                "taskType": request.taskType.value,
                "messages": messages,
                "finalResult": final_result.value,
                "createdAt": datetime.utcnow()
            }
            result = await tutor_chats_collection.insert_one(chat_doc)
            chat_id = str(result.inserted_id)
        
        return {
            "result": EvaluationResult.PASS if result == "PASS" else EvaluationResult.FAIL,
            "feedback": feedback,
            "hint": hint,
            "answerRevealed": answer_revealed,
            "chatId": chat_id
        }
        
    except Exception as e:
        logger.error(f"Error evaluating response: {e}")
        raise Exception(f"Failed to evaluate response: {str(e)}")

def _build_system_prompt(task_type: TaskType, word: dict) -> str:
    """Build system prompt for AI tutor"""
    base_prompt = """You are a vocabulary tutor evaluating student responses. 
Your role is to assess whether the student's answer demonstrates understanding of the word.
Be encouraging but accurate. Accept paraphrases and similar meanings.
Reject vague, circular, or incorrect definitions."""
    
    if task_type == TaskType.MEANING:
        return f"""{base_prompt}
The student should provide the meaning of the word: {word.get('word')}
Correct meaning: {word.get('meaning')}"""
    
    elif task_type == TaskType.SENTENCE:
        return f"""{base_prompt}
The student should create a sentence using the word: {word.get('word')}
Example sentence: {word.get('example')}"""
    
    elif task_type == TaskType.MCQ:
        return f"""{base_prompt}
The student should select the correct meaning for: {word.get('word')}
Correct meaning: {word.get('meaning')}"""
    
    elif task_type == TaskType.PARAGRAPH:
        return f"""{base_prompt}
The student should write a paragraph using the word: {word.get('word')}
The word's meaning: {word.get('meaning')}
Example: {word.get('example')}"""
    
    return base_prompt

def _build_evaluation_prompt(
    word: dict,
    task_type: TaskType,
    user_response: str,
    failure_count: int
) -> str:
    """Build evaluation prompt for OpenAI"""
    prompt = f"""Evaluate this student response for the word "{word.get('word')}".

Word meaning: {word.get('meaning')}
Example: {word.get('example')}
Task type: {task_type.value}
Student response: {user_response}

Evaluation rules:
- Accept paraphrases and similar meanings
- Reject vague or circular definitions
- Be encouraging but accurate

Return a JSON object with this structure:
{{
    "result": "PASS" or "FAIL",
    "feedback": "Detailed feedback message",
    "hint": "Optional hint if FAIL (only on first failure)",
    "answerRevealed": true/false (true only on second failure)
}}

Failure count so far: {failure_count}
"""
    
    if failure_count == 0:
        prompt += "\nThis is the first attempt. If FAIL, provide a hint but don't reveal the answer."
    elif failure_count == 1:
        prompt += "\nThis is the second attempt. If FAIL, reveal the correct answer."
    
    return prompt
