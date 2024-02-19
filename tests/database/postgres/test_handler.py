import pytest

from src.models.quiz_models import Choice, Question


@pytest.mark.asyncio(scope="session")
async def test_create_question(postgres, question_item_schema):
    created_question = await postgres.create_question(question_item_schema)

    # Check if the question is created successfully
    assert created_question.question_text == "What is the capital of France?"
    assert len(created_question.choices) == 3

    questions = await postgres.get_all_questions()
    # Check if questions are retrieved successfully
    assert len(questions) == 1


@pytest.mark.asyncio(scope="session")
async def test_duplicate_question_creation(postgres, question_item_schema):
    # Attempt to create the second question with the same question text
    with pytest.raises(ValueError) as exc_info:
        await postgres.create_question(question_item_schema)

    # Check if the error message indicates a duplicate question
    assert "A question with this text already exists." in str(exc_info.value)


@pytest.mark.asyncio(scope="session")
async def test_get_all_questions(postgres):
    # Create some test questions
    question1 = Question(question_text="Question #1")
    question2 = Question(question_text="Question #2")
    async with postgres.session_factory() as session:
        session.add_all([question1, question2])
        await session.commit()

    # Retrieve all questions
    questions = await postgres.get_all_questions(search_text="Question #")
    # Check if questions are retrieved successfully
    assert len(questions) == 2
    assert all(isinstance(q, Question) for q in questions)


@pytest.mark.asyncio(scope="session")
async def test_get_question_by_id(postgres):
    # Create a test question
    question = Question(question_text="Test first question")
    async with postgres.session_factory() as session:
        session.add(question)
        await session.commit()

    # Retrieve the question by its ID
    retrieved_question = await postgres.get_question_by_id(question.id)
    # Check if the question is retrieved successfully
    assert retrieved_question.question_text == "Test first question"


@pytest.mark.asyncio(scope="session")
async def test_get_question_answer(postgres):
    # Create a test question with a correct choice
    question = Question(question_text="Test second question")
    choice = Choice(choice_text="Correct choice", is_correct=True)
    question.choices.append(choice)
    async with postgres.session_factory() as session:
        session.add(question)
        await session.commit()

    # Retrieve the correct choice for the question
    answer = await postgres.get_question_answer(question.id)
    # Check if the correct choice is retrieved successfully
    assert answer.choice_text == "Correct choice"


@pytest.mark.asyncio(scope="session")
async def test_check_question_answer(postgres):
    # Create a test question with a correct choice
    question = Question(question_text="Test third question")
    choice = Choice(choice_text="Correct choice", is_correct=True)
    question.choices.append(choice)
    async with postgres.session_factory() as session:
        session.add(question)
        await session.commit()

    # Check if the correct choice is validated
    correct_choice = await postgres.check_question_answer(
        question_id=question.id, answer_id=choice.id
    )
    # Check if the correct choice is validated successfully
    assert correct_choice is not None

    # Check if an incorrect choice is validated
    incorrect_choice = await postgres.check_question_answer(
        question_id=question.id, answer_id=99999
    )
    # Check if the incorrect choice is not validated
    assert incorrect_choice is None
