from fastapi import APIRouter, Depends, HTTPException, status
from app.models.tutor_chat import TutorEvaluationRequest, TutorEvaluationResponse
from app.middleware.auth_middleware import get_current_user
from app.services.tutor_service import evaluate_response

router = APIRouter(prefix="/api/tutor", tags=["Tutor"])

@router.post("/evaluate", response_model=TutorEvaluationResponse)
async def evaluate_endpoint(
    request: TutorEvaluationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Evaluate user response using AI tutor"""
    try:
        return await evaluate_response(current_user["user_id"], request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
