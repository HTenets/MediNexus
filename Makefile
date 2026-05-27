.PHONY: dev dev-backend dev-frontend db-migrate db-upgrade docker-up

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
	cd backend && pip install -e .
	cd frontend && npm install

init-db:
	cd backend && python scripts/init_db.py
