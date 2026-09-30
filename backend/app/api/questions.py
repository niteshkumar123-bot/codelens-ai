from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.models.models import Question
from app.schemas.schemas import QuestionGenerateRequest, QuestionResponse
from app.llm.provider import LLMProvider

router = APIRouter(prefix="/questions", tags=["questions"])

@router.post("/generate", response_model=List[QuestionResponse])
def generate_questions(payload: QuestionGenerateRequest, db: Session = Depends(get_db)):
    prompt = f"Generate a Python coding question about {payload.topic} with difficulty {payload.difficulty} focusing on concepts {', '.join(payload.concepts)}. Return valid JSON with keys: title, topic, difficulty, problem_statement, constraints, examples."
    raw_resp = LLMProvider.generate_completion(prompt)
    
    # Store in DB
    question = Question(
        title=f"{payload.difficulty.capitalize()} {payload.topic.capitalize()} Challenge",
        topic=payload.topic,
        difficulty=payload.difficulty,
        problem_statement=raw_resp,
        constraints="Time Limit: 1.0s, Memory Limit: 256MB",
        examples=[{"input": "nums = [2, 7, 11, 15], target = 9", "output": "[0, 1]"}]
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return [question]

@router.get("/", response_model=List[QuestionResponse])
def list_questions(db: Session = Depends(get_db)):
    return db.query(Question).all()
