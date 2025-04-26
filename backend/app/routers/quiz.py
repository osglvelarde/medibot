from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_quiz():
    return {"message": "Quiz endpoint working"}
