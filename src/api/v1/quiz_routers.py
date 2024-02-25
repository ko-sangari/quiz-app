from fastapi import APIRouter, Body, Depends, HTTPException
from typing import List, Optional

from src.api.dependencies import get_postgres_dependency
from src.database.postgres.handler import PostgreSQLHandler
from src.schemas.quiz_schemas import (
    AnswerResponse,
    ChoiceResponse,
    QuestionResponse,
    QuestionSchema,
)

router = APIRouter(
    prefix="/quiz",
    tags=["quiz"],
)


@router.post("/questions", response_model=QuestionResponse)
async def create_question(
    request: QuestionSchema = Body(...),
    postgres: PostgreSQLHandler = Depends(get_postgres_dependency),
) -> QuestionResponse:
    """
    Creates a new question with the provided details and choices.

    Args:
        request (QuestionSchema): The schema of the question to be created.

    Returns:
        QuestionResponse: The created question with its details and choices.
    """
    try:
        return await postgres.create_question(request)  # type: ignore
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/questions", response_model=List[QuestionResponse])
async def get_all_questions(
    postgres: PostgreSQLHandler = Depends(get_postgres_dependency),
) -> List[QuestionResponse]:
    """
    Retrieves a list of all questions and their associated choices.

    Returns:
        List[QuestionResponse]: A list of questions with their details and choices.
    """
    return await postgres.get_all_questions()  # type: ignore


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int, postgres: PostgreSQLHandler = Depends(get_postgres_dependency)
) -> QuestionResponse:
    """
    Retrieves a single question and its associated choices based on the question ID.

    Args:
        question_id (int): The unique identifier of the question.

    Returns:
        QuestionResponse: The requested question with its details and choices.

    Raises:
        HTTPException: A 404 error if the question is not found.
    """
    if question := await postgres.get_question_by_id(question_id):
        return question  # type: ignore
    raise HTTPException(status_code=404, detail="Question not found!")


@router.get("/questions/{question_id}/answer", response_model=Optional[ChoiceResponse])
async def get_question_answer(
    question_id: int, postgres: PostgreSQLHandler = Depends(get_postgres_dependency)
) -> ChoiceResponse:
    """
    Retrieves the correct answer for a specified question.

    Args:
        question_id (int): The unique identifier of the question.

    Returns:
        ChoiceResponse: The correct choice for the specified question.
    """
    if answer := await postgres.get_question_answer(question_id):
        return answer
    raise HTTPException(status_code=404, detail="Question not found!")


@router.get(
    "/questions/{question_id}/answer/{answer_id}", response_model=AnswerResponse
)
async def check_question_answer(
    question_id: int,
    answer_id: int,
    postgres: PostgreSQLHandler = Depends(get_postgres_dependency),
) -> AnswerResponse:
    """
    Checks if the provided answer ID is the correct choice for the specified question ID.

    Args:
        question_id (int): The unique identifier of the question.
        answer_id (int): The unique identifier of the provided answer.

    Returns:
        AnswerResponse: A response indicating whether the provided answer is correct or not.
    """
    answer = await postgres.check_question_answer(question_id, answer_id)
    return AnswerResponse(
        is_correct=answer is not None,
        message="Congrats!!!" if answer is not None else "NO!",
    )
