from datetime import datetime, date
from bson import ObjectId
import random
import logging
from app.database import (
    get_users_collection,
    get_words_collection,
    get_daily_tasks_collection,
    get_cron_runs_collection
)
from app.models.daily_task import TaskType, TaskStatus
from typing import List

logger = logging.getLogger(__name__)

async def generate_daily_tasks():
    """Generate daily tasks for all active users"""
    users_collection = get_users_collection()
    cron_runs_collection = get_cron_runs_collection()
    
    run_at = datetime.utcnow()
    stats = {
        "usersProcessed": 0,
        "tasksCreated": 0,
        "wordsMoved": 0,
        "errors": []
    }
    
    try:
        # Get all active users
        active_users = await users_collection.find({"isActive": True}).to_list(length=None)
        
        for user in active_users:
            try:
                user_id = str(user["_id"])
                today = date.today().isoformat()
                
                # Generate tasks for this user
                result = await generate_daily_tasks_for_user(user_id, today)
                
                stats["usersProcessed"] += 1
                stats["tasksCreated"] += result.get("tasksCreated", 0)
                
            except Exception as e:
                error_msg = f"Error processing user {user.get('email', 'unknown')}: {str(e)}"
                logger.error(error_msg)
                stats["errors"].append(error_msg)
        
        # Log successful run
        await cron_runs_collection.insert_one({
            "runAt": run_at,
            "status": "SUCCESS",
            "stats": stats,
            "errorLog": None
        })
        
        logger.info(f"Daily task generation completed. Stats: {stats}")
        
    except Exception as e:
        error_msg = f"Critical error in daily task generation: {str(e)}"
        logger.error(error_msg)
        
        # Log failed run
        await cron_runs_collection.insert_one({
            "runAt": run_at,
            "status": "FAILED",
            "stats": stats,
            "errorLog": error_msg
        })
        
        raise

async def generate_daily_tasks_for_user(user_id: str, task_date: str) -> dict:
    """Generate daily tasks for a specific user"""
    words_collection = get_words_collection()
    daily_tasks_collection = get_daily_tasks_collection()
    
    # Check if tasks already exist for this date
    existing = await daily_tasks_collection.find_one({
        "userId": ObjectId(user_id),
        "date": task_date
    })
    
    if existing:
        logger.info(f"Tasks already exist for user {user_id} on {task_date}")
        return {"tasksCreated": 0}
    
    # Get ACTIVE words grouped by priority
    words_by_priority = {
        1: [],
        2: [],
        3: [],
        4: []
    }
    
    active_words = await words_collection.find({
        "userId": ObjectId(user_id),
        "state": "ACTIVE"
    }).to_list(length=None)
    
    for word in active_words:
        priority = word.get("priority", 1)
        if priority in words_by_priority:
            words_by_priority[priority].append(word)
    
    # Select words per priority
    # P1 → 1 word (MEANING)
    # P2 → 2 words (SENTENCE)
    # P3 → 3 words (MCQ)
    # P4 → 2 words (PARAGRAPH)
    
    selected_words = {
        1: _select_words(words_by_priority[1], 1),
        2: _select_words(words_by_priority[2], 2),
        3: _select_words(words_by_priority[3], 3),
        4: _select_words(words_by_priority[4], 2)
    }
    
    # Create tasks
    tasks = []
    task_id_counter = 1
    
    # P1 - MEANING task
    if selected_words[1]:
        tasks.append({
            "taskId": f"task_{task_id_counter}",
            "type": TaskType.MEANING.value,
            "wordIds": [str(word["_id"]) for word in selected_words[1]],
            "status": TaskStatus.PENDING.value,
            "result": None
        })
        task_id_counter += 1
    
    # P2 - SENTENCE task
    if selected_words[2]:
        tasks.append({
            "taskId": f"task_{task_id_counter}",
            "type": TaskType.SENTENCE.value,
            "wordIds": [str(word["_id"]) for word in selected_words[2]],
            "status": TaskStatus.PENDING.value,
            "result": None
        })
        task_id_counter += 1
    
    # P3 - MCQ task
    if selected_words[3]:
        tasks.append({
            "taskId": f"task_{task_id_counter}",
            "type": TaskType.MCQ.value,
            "wordIds": [str(word["_id"]) for word in selected_words[3]],
            "status": TaskStatus.PENDING.value,
            "result": None
        })
        task_id_counter += 1
    
    # P4 - PARAGRAPH task
    if selected_words[4]:
        tasks.append({
            "taskId": f"task_{task_id_counter}",
            "type": TaskType.PARAGRAPH.value,
            "wordIds": [str(word["_id"]) for word in selected_words[4]],
            "status": TaskStatus.PENDING.value,
            "result": None
        })
        task_id_counter += 1
    
    # Update lastReviewedAt for selected words
    all_selected_word_ids = []
    for priority_words in selected_words.values():
        for word in priority_words:
            all_selected_word_ids.append(word["_id"])
    
    if all_selected_word_ids:
        await words_collection.update_many(
            {"_id": {"$in": all_selected_word_ids}},
            {"$set": {"lastReviewedAt": datetime.utcnow()}}
        )
    
    # Create daily_tasks document
    if tasks:
        await daily_tasks_collection.insert_one({
            "userId": ObjectId(user_id),
            "date": task_date,
            "tasks": tasks,
            "createdAt": datetime.utcnow()
        })
    
    return {"tasksCreated": len(tasks)}

def _select_words(words: List[dict], count: int) -> List[dict]:
    """Select random words from list, up to count"""
    if len(words) <= count:
        return words
    return random.sample(words, count)
