import logging

from sqlalchemy.engine.url import URL
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import List, Optional

from src.database.postgres.core import PostgreSQLCore
from src.models.quiz_models import Choice, Question
from src.schemas.quiz_schemas import ChoiceResponse, QuestionSchema

logger = logging.getLogger(__name__)


class PostgreSQLHandler(PostgreSQLCore):
    """
    A subclass of PostgreSQLHandler to handle database queries.
    """

    def __init__(self, db_url: URL = None, database: str = None) -> None:
        """
        Initializes the PostgreSQLCore with a database URL and connects to it.

        Args:
            db_url (str, optional): The database URL. Defaults to None.
            database (str, optional): The name of the database to connect to. Defaults to None.
        """
        super().__init__(db_url, database)

    async def create_question(self, question: QuestionSchema) -> Question:
        """
        Creates a new question along with its choices in the database.

        Args:
            question (QuestionSchema): The schema of the question to be created.

        Returns:
            Question: The created Question object.
        """
        question_object = Question(question_text=question.question_text)
        for choice_schema in question.choices:
            _choice = Choice(
                choice_text=choice_schema.choice_text,
                is_correct=choice_schema.is_correct,
            )
            question_object.choices.append(_choice)

        async with self.session_factory() as session:
            try:
                session.add(question_object)
                await session.commit()
                await session.refresh(question_object, attribute_names=["choices"])
                return question_object
            except IntegrityError:
                await session.rollback()  # Rollback the transaction
                raise ValueError("A question with this text already exists.")

    async def get_all_questions(self, search_text: str = None) -> List[Question]:
        """
        Retrieves all questions from the database, including their choices.

        Args:
            search_text (str, optional): A string to search for in question_text. Defaults to None.

        Returns:
            List[Question]: A list of all questions with their choices.
        """
        async with self.session_factory() as session:
            query = select(Question).options(joinedload(Question.choices))
            if search_text:
                query = query.filter(Question.question_text.ilike(f"%{search_text}%"))
            questions = await session.execute(query)
            return list(questions.unique().scalars().all())

    async def get_question_by_id(self, question_id: int) -> Optional[Question]:
        """
        Retrieves a question by its ID, including its choices.

        Args:
            question_id (int): The ID of the question to be retrieved.

        Returns:
            Optional[Question]: The retrieved Question object, or None if not found.
        """
        async with self.session_factory() as session:
            query = (
                select(Question)
                .options(joinedload(Question.choices))
                .filter(Question.id == question_id)
            )
            question = (await session.execute(query)).scalar()
        return question if question else None

    async def get_question_answer(self, question_id: int) -> ChoiceResponse:
        """
        Retrieves the correct choice for a given question ID.

        Args:
            question_id (int): The ID of the question.

        Returns:
            ChoiceResponse: The correct choice for the question.
        """
        async with self.session_factory() as session:
            query = select(Choice).filter(
                Choice.question_id == question_id, Choice.is_correct.is_(True)
            )
            answer = (await session.execute(query)).scalar()
        return answer  # type: ignore

    async def check_question_answer(self, question_id: int, answer_id: int) -> Choice:
        """
        Checks if the provided answer ID is correct for the given question ID.

        Args:
            question_id (int): The ID of the question.
            answer_id (int): The ID of the answer to check.

        Returns:
            Choice: The correct choice if the answer is correct, otherwise None.
        """
        async with self.session_factory() as session:
            query = select(Choice).filter(
                Choice.question_id == question_id,
                Choice.id == answer_id,
                Choice.is_correct.is_(True),
            )
            answer = (await session.execute(query)).scalar()
        return answer if answer else None
