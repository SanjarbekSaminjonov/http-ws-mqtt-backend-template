ls:
	echo "Available make commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {print $$1 "\t" $$2}'

run_infra: ## Run infrastructure services using Docker Compose
	docker compose -p infra -f docker-compose.infra.yml up -d

down_infra: ## Stop infrastructure services using Docker Compose
	docker compose -p infra -f docker-compose.infra.yml down

run_app: ## Run Django application using Docker Compose
	docker compose -p app -f docker-compose.app.yml up -d --build

down_app: ## Stop Django application using Docker Compose
	docker compose -p app -f docker-compose.app.yml down