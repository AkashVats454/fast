from fastapi import FastAPI, status, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from custom import auth
import logging


app = FastAPI()
app.include_router(auth.router)
models.Base.metadata.create_all(bind=engine)
logger = logging.getLogger(__name__)
logger.info(f"starting the app")
user_dependency = Annotated[dict, Depends(auth.get_current_user)]


class ChoiceBase(BaseModel):
    choice_text: str
    is_correct: bool


class QuestionBase(BaseModel):
    question_text: str
    choices: List[ChoiceBase]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/questions/{question_id}")
async def get_question(question_id: int, db: db_dependency, user: user_dependency):
    result = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not result:
        return HTTPException(status_code=404, detail=f"Question for id {question_id} doesn't exist")
    return result


@app.get("/choices/{question_id}")
async def get_choices(question_id: int, db: db_dependency, user: user_dependency):
    result = db.query(models.Choices).filter(models.Choices.question_id == question_id).all()
    if not result:
        return HTTPException(status_code=404, detail=f"Choices for Question id {question_id} doesn't exist")
    return result


@app.post("/questions/")
async def create_questions(question: QuestionBase, db: db_dependency, user: user_dependency):
    db_question = models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    for choice in question.choices:
        db_choice = models.Choices(choice_text=choice.choice_text, is_correct=choice.is_correct, question_id=db_question.id)
        db.add(db_choice)
    db.commit()


@app.get("/user", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed!")
    return {"User": user}

