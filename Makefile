.PHONY: help run build sqlc migrate-up migrate-down tidy test

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n",$$1,$$2}'

run: ## Run the server locally (loads .env if you `set -a; source .env; set +a`)
	go run ./cmd/server

build: ## Build a static server binary into bin/
	CGO_ENABLED=0 go build -o bin/site-backend ./cmd/server

sqlc: ## Regenerate type-safe DB code from db/queries + db/migrations
	sqlc generate

migrate-up: ## Apply all migrations (needs golang-migrate + $DATABASE_URL)
	migrate -path db/migrations -database "$(DATABASE_URL)" up

migrate-down: ## Roll back the most recent migration
	migrate -path db/migrations -database "$(DATABASE_URL)" down 1

tidy: ## Tidy and verify go modules
	go mod tidy

test: ## Run the test suite
	go test ./...
