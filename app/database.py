import logging
import os
import time

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

logger = logging.getLogger("task-api.database")


def _require_env(name: str) -> str:
    """Read a required environment variable or fail fast with a clear message."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


# Credentials come ONLY from environment variables - nothing is hardcoded.
DB_HOST = _require_env("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = _require_env("DB_NAME")
DB_USER = _require_env("DB_USER")
DB_PASSWORD = _require_env("DB_PASSWORD")

# URL.create() safely escapes special characters in the password.
DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # test connections before use (important for RDS failover)
    pool_recycle=280,     # recycle connections before idle timeouts close them
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: one DB session per request, always closed afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_db(retries: int = 30, delay: float = 2.0) -> None:
    """Block until the database accepts connections (or give up)."""
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established")
            return
        except Exception as exc:
            logger.warning(
                "Database not ready (attempt %s/%s): %s", attempt, retries, exc
            )
            time.sleep(delay)
    raise RuntimeError("Could not connect to the database after multiple attempts")
