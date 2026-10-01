# task-management-app-using-fastapi
# Task Management API

FastAPI + SQLAlchemy + MySQL, containerized with Docker Compose.

## Run

    cp .env.example .env
    docker compose up -d --build

- API docs:  http://localhost:8000/docs
- Health:    http://localhost:8000/health
- DB health: http://localhost:8000/health/db

## Stop

    docker compose down        # keep data
    docker compose down -v     # delete data too

## Configuration

All settings come from environment variables: DB_HOST, DB_PORT, DB_NAME,
DB_USER, DB_PASSWORD (plus DB_ROOT_PASSWORD for the local MySQL container
and AUTO_CREATE_TABLES). See `.env.example`.

## Endpoints

| Method | Path          | Description        |
|--------|---------------|--------------------|
| POST   | /tasks        | Create a task      |
| GET    | /tasks        | List tasks         |
| GET    | /tasks/{id}   | Get a task         |
| PUT    | /tasks/{id}   | Update a task      |
| DELETE | /tasks/{id}   | Delete a task      |
| GET    | /health       | Liveness check     |
| GET    | /health/db    | DB readiness check |
