build:
	python -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install "fastapi[standard]" "uvicorn[standard]" python-dotenv structlog sqlalchemy alembic asyncpg
	venv/bin/alembic init alembic

run:
	venv/bin/uvicorn main:app --host localhost --port 8000 --reload

migrate:
	venv/bin/alembic revision --autogenerate -m "New migration"
	venv/bin/alembic upgrade head