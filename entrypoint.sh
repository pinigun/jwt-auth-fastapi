alembic init src/infrastructure/database/migrations
alembic revision --autogenerate -m "init"
alembic upgrade head
uvicorn src.infrastructure.api.app:app --host 0.0.0.0 --port 8000 --reload
