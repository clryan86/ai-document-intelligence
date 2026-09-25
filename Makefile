.PHONY: install dev test lint run docker

install:
	python -m pip install -r requirements-dev.txt

dev:
	uvicorn app.main:app --reload

test:
	pytest

lint:
	ruff check .
	ruff format --check .

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

docker:
	docker compose up --build
