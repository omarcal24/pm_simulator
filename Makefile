.PHONY: dev dev-backend dev-frontend install-backend install-frontend migrate seed test lint

# Backend (use venv: source .venv/bin/activate first, or run via make)
install-backend:
	python3 -m venv .venv 2>/dev/null || true
	.venv/bin/pip install -r backend/requirements.txt

migrate:
	cd backend && ../.venv/bin/python manage.py migrate

seed:
	cd backend && ../.venv/bin/python manage.py seed_scenarios

dev-backend:
	cd backend && ../.venv/bin/python manage.py runserver

# Frontend
install-frontend:
	cd frontend && npm install

dev-frontend:
	cd frontend && npm run dev

# Combined dev (run in separate terminals)
dev:
	@echo "Run 'make dev-backend' in one terminal and 'make dev-frontend' in another"

# Bootstrap: install deps, migrate, seed
bootstrap: install-backend migrate seed install-frontend
	@echo "Backend ready. Create a user with: cd backend && python manage.py createsuperuser"
	@echo "Then run 'make dev-backend' and 'make dev-frontend'"

test:
	cd backend && ../.venv/bin/python manage.py test
	cd frontend && npm run build
