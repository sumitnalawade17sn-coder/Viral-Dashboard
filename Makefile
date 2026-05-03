.PHONY: seed backend

seed:
	cd backend && source .venv/bin/activate && python -m app.seed

backend:
	cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000
