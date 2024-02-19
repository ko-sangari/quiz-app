import pytest

from sqlalchemy import select

from src.models.quiz_models import Question


@pytest.mark.asyncio(scope="session")
async def test_quesion_create(postgres, question_item):
    async with postgres.session_factory() as session:
        session.add(question_item)
        await session.commit()

        query_all = (await session.execute(select(Question))).scalars().all()
        assert len(query_all) == 1


@pytest.mark.asyncio(scope="session")
async def test_create_tables(postgres):
    async with postgres.session_factory() as session:
        async with session.bind.connect() as connection:
            table_names = await connection.run_sync(
                session.bind.dialect.get_table_names
            )
            assert table_names == ["questions", "choices"]


@pytest.mark.asyncio(scope="session")
async def test_health_check(postgres):
    result = await postgres.health_check()
    assert result is True


@pytest.mark.asyncio(scope="session")
async def test_drop_tables(postgres):
    await postgres.drop_tables()

    async with postgres.session_factory() as session:
        async with session.bind.connect() as connection:
            table_names = await connection.run_sync(
                session.bind.dialect.get_table_names
            )
            assert table_names == []

    await postgres.create_tables()
