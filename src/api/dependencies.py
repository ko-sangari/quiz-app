from src.database.postgres.handler import PostgreSQLHandler


async def get_postgres_dependency() -> PostgreSQLHandler:
    db_handler = PostgreSQLHandler()
    await db_handler.initialize()
    return db_handler
