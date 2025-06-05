# Justfile for Messaging API Backend Assignment
set shell := ["bash", "-cu"]

# Install Python dependencies
install:
	pip install -r requirements.txt

# Run the FastAPI app
dev:
	uvicorn app.main:app --reload

# Start services using Docker Compose
up:
	docker-compose up -d

# Stop services
down:
	docker-compose down

# Run database migrations (if using Alembic)
createdb:
	python app/scripts/create_db.py

revision message:
	alembic revision --autogenerate -m "{{message}}"

migrate:
	alembic upgrade head

# Run tests
test:
	pytest

# Format code using black and isort
format:
	black .
	isort .

# Run the MCP server (optional)
mcp:
	uvicorn app.mcp_server:app --reload