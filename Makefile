.ONESHELL:
VENV ?= venv
SYS_PYTHON ?= python
VENV_PYTHON ?= $(VENV)/bin/python

create_$(VENV):
	$(SYS_PYTHON) -m venv $(VENV)
	chmod +x $(VENV)/bin/activate

activate_$(VENV):
	. ./$(VENV)/bin/activate

build: activate_$(VENV) requirements.txt
	pip install --upgrade pip
	pip install -r requirements.txt

run: activate_$(VENV)
	uvicorn main:app --host localhost --port 8000 --reload

new_migration: activate_$(VENV)
	alembic revision --autogenerate -m "new_migration"

migrate: activate_$(VENV)
	alembic upgrade head