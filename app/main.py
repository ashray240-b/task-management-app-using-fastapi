import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app import models  # noqa: F401  (registers the Task model with SQLAlchemy)
from app.database import Base, engine, wait_for_db
from app.routes import tasks

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("task-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once at startup.
    wait_for_db()
    if os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true":
        Base.metadata.create_all(bind=engine)  # creates missing tables only
        logger.info("Database tables are ready")
    yield
    # Runs at shutdown.
    engine.dispose()


app = FastAPI(
    title="Task Management API",
    description="Simple task CRUD API used for the AWS Disaster Recovery project",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(tasks.router)


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request: Request, exc: SQLAlchemyError):
    # Log details server-side, return a generic message to the client.
    logger.exception("Database error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=503,
        content={"detail": "Database temporarily unavailable. Please retry."},
    )


@app.get("/health", tags=["Health"])
def health():
    """Liveness check - does NOT touch the database (use this for the ALB)."""
    return {"status": "healthy"}


@app.get("/health/db", tags=["Health"])
def health_db():
    """Readiness check - verifies the database connection."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        logger.exception("Database health check failed")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "unreachable"},
        )
