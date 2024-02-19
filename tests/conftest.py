import pytest_asyncio

from fastapi import FastAPI
from httpx import AsyncClient
from typing import AsyncGenerator, Callable

from src.database.postgres.handler import PostgreSQLHandler
from src.models.quiz_models import Question, Choice
from src.schemas.quiz_schemas import QuestionSchema, ChoiceSchema


@pytest_asyncio.fixture(scope="module")
async def override_get_postgres_dependency() -> Callable:
    async def _override_get_postgres_dependency():
        db_handler = PostgreSQLHandler(database="test_quiz_db")
        await db_handler.initialize()
        return db_handler

    return _override_get_postgres_dependency


@pytest_asyncio.fixture(scope="module")
async def app(override_get_postgres_dependency: Callable) -> AsyncGenerator:
    from src.api.dependencies import get_postgres_dependency
    from src.main import app

    app.dependency_overrides[get_postgres_dependency] = override_get_postgres_dependency
    yield app
    db_handler = PostgreSQLHandler(database="test_quiz_db")
    await db_handler.drop_tables()
    await db_handler.engine.dispose()


@pytest_asyncio.fixture(scope="module")
async def async_client_v1(app: FastAPI) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url="http://testserver/v1") as async_client:
        yield async_client


@pytest_asyncio.fixture(scope="session")
async def postgres():
    db_handler = PostgreSQLHandler(database="test_quiz_db")
    await db_handler.initialize()
    yield db_handler

    # Perform cleanup after all tests are done
    await db_handler.drop_tables()
    await db_handler.engine.dispose()


@pytest_asyncio.fixture(scope="session")
def question_item():
    return Question(
        question_text="What is the capital of France?",
        choices=[
            Choice(choice_text="Paris", is_correct=True),
            Choice(choice_text="Berlin", is_correct=False),
            Choice(choice_text="London", is_correct=False),
        ],
    )


@pytest_asyncio.fixture(scope="session")
def question_item_schema():
    return QuestionSchema(
        question_text="What is the capital of France?",
        choices=[
            ChoiceSchema(choice_text="Paris", is_correct=True),
            ChoiceSchema(choice_text="Berlin", is_correct=False),
            ChoiceSchema(choice_text="London", is_correct=False),
        ],
    )


@pytest_asyncio.fixture(scope="session")
def question_item_json():
    return {
        "question_text": "What is the capital of France?",
        "choices": [
            {"choice_text": "Paris", "is_correct": True},
            {"choice_text": "Berlin", "is_correct": False},
            {"choice_text": "London", "is_correct": False},
        ],
    }
