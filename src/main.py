from logging import config, getLogger

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.api.v1.quiz_routers import router as v1_quiz_router
from src.database.postgres.handler import PostgreSQLHandler

# setup logger
config.fileConfig("logging.conf", disable_existing_loggers=False)  # type: ignore
logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup-event

    db_handler = PostgreSQLHandler()
    await db_handler.initialize()
    logger.info(f"Database Health-Check: {await db_handler.health_check()}")

    yield

    # shutdown-event


app = FastAPI(lifespan=lifespan)

app.include_router(v1_quiz_router, prefix="/v1")


@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def docs():
    return RedirectResponse(url="/docs")
