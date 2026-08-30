.PHONY: dev dev-backend dev-frontend db-migrate db-upgrade docker-up test test-unit test-integration

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

db-migrate:
	cd backend && alembic revision --autogenerate -m "$(msg)"

db-upgrade:
	cd backend && alembic upgrade head

db-downgrade:
	cd backend && alembic downgrade -1

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

install:
	pip install -e ".[dev]"
	cd frontend && npm install

init-db:
	PYTHONPATH=backend python scripts/init_db.py

test:
	python -m pytest tests/ -v

test-unit:
	python -m pytest tests/unit/ -v

test-integration:
	python -m pytest tests/integration/ -v
