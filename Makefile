# Forbes Advisor - Project Makefile
# Note: Indentation MUST be a hard Tab character, not spaces.

.PHONY: default help install setup-local quick-start test clean docker-up docker-down copy-envs

# --- DEFAULT TARGET ---
default: quick-start

help:
	@echo "Available commands:"
	@echo "  make        - (Default) Copy envs, Docker build, migrate, and seed"
	@echo "  copy-envs   - Initialize .env files from examples in all 3 locations"
	@echo "  install     - Install Python and Node.js dependencies locally"
	@echo "  setup-local - Full local setup (install + migrate + seed)"
	@echo "  test        - Run backend and frontend tests"
	@echo "  docker-down - Stop and remove Docker containers/volumes"

# --- ENVIRONMENT SETUP ---

copy-envs:
	@echo "📝 Initializing environment files..."
	@test -f .env || cp .env.example .env
	@test -f backend/.env || cp backend/.env.example backend/.env
	@test -f frontend/.env || cp frontend/.env.example frontend/.env
	@echo "✅ Environment files ready."

# --- DOCKER WORKFLOW ---

# Build and start services (Ensures envs exist first)
docker-up: copy-envs
	@echo "🐳 Building and starting Docker services..."
	docker compose up -d --build

# The full bootstrap process
quick-start: docker-up
	@echo "⏳ Waiting for Database to initialize..."
	@sleep 10
	@echo "🗄️ Running Migrations..."
	docker compose exec -T backend python manage.py migrate
	@echo "🌱 Seeding 1,000,000 rows from Parquet..."
	docker compose exec -T backend python manage.py seed_data
	@echo "✅ SUCCESS! App is live at http://localhost:3000"

# --- LOCAL DEVELOPMENT WORKFLOW (Non-Docker) ---

install: copy-envs
	@echo "📦 Installing local dependencies..."
	cd backend && pip install -r requirements.txt
	cd frontend && pnpm install

setup-local: install
	@echo "🗄️ Running local migrations..."
	cd backend && python manage.py migrate
	@echo "🌱 Running local seed..."
	cd backend && python manage.py seed_data

# --- TESTING & UTILS ---

test:
	@echo "🧪 Running tests..."
	docker compose exec -T backend pytest

docker-down:
	@echo "🐳 Stopping Docker services..."
	docker compose down -v

clean:
	@echo "🧹 Cleaning up caches..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf frontend/.next
	@echo "✅ Cleanup complete."