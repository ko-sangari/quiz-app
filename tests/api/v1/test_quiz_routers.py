import pytest

from fastapi import status


@pytest.mark.asyncio(scope="module")
async def test_create_question(async_client_v1, question_item_json):
    response = await async_client_v1.post("/quiz/questions", json=question_item_json)

    assert response.status_code == status.HTTP_200_OK
    api_response = response.json()
    assert api_response["question_text"] == question_item_json["question_text"]
    assert len(api_response["choices"]) == len(question_item_json["choices"])
    for choice, expected_choice in zip(
        api_response["choices"], question_item_json["choices"]
    ):
        assert choice["choice_text"] == expected_choice["choice_text"]
        assert choice["is_correct"] == expected_choice["is_correct"]


@pytest.mark.asyncio(scope="module")
async def test_create_question_duplicate(async_client_v1, question_item_json):
    response = await async_client_v1.post("/quiz/questions", json=question_item_json)
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio(scope="module")
async def test_get_all_questions(async_client_v1):
    response = await async_client_v1.get("/quiz/questions")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


@pytest.mark.asyncio(scope="module")
async def test_get_question_by_id(async_client_v1, question_item_json):
    response = await async_client_v1.get("/quiz/questions/1")
    assert response.status_code == status.HTTP_200_OK
    api_response = response.json()
    assert api_response["question_text"] == question_item_json["question_text"]
    assert len(api_response["choices"]) == len(question_item_json["choices"])

    response = await async_client_v1.get("/quiz/questions/10")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    api_response = response.json()
    assert api_response["detail"] == "Question not found!"


@pytest.mark.asyncio(scope="module")
async def test_get_question_answer(async_client_v1, question_item_json):
    response = await async_client_v1.get("/quiz/questions/1/answer")
    assert response.status_code == status.HTTP_200_OK
    api_response = response.json()
    assert api_response["is_correct"]
    assert api_response["choice_text"] == "Paris"

    response = await async_client_v1.get("/quiz/questions/10/answer")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    api_response = response.json()
    assert api_response["detail"] == "Question not found!"


@pytest.mark.asyncio(scope="module")
async def test_check_question_answer(async_client_v1, question_item_json):
    response = await async_client_v1.get("/quiz/questions/1/answer/1")
    assert response.status_code == status.HTTP_200_OK
    api_response = response.json()
    assert api_response["is_correct"]

    response = await async_client_v1.get("/quiz/questions/1/answer/2")
    assert response.status_code == status.HTTP_200_OK
    api_response = response.json()
    assert not api_response["is_correct"]
