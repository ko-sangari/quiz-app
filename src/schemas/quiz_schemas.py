from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class ChoiceSchema(BaseModel):
    choice_text: str
    is_correct: bool


class QuestionSchema(BaseModel):
    question_text: str
    choices: List[ChoiceSchema]


class ChoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    choice_text: str
    is_correct: bool


class QuestionResponse(BaseModel):
    id: int
    question_text: str
    choices: List[ChoiceResponse]


class AnswerResponse(BaseModel):
    is_correct: bool
    message: Optional[str] = None
