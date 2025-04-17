# HELP

.PHONY: help

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
HEAD = 1

run-server: ## Run docker compose up as deamon
	docker compose up -d

run-server-build: ## Run Server build
	docker compose up -d --build

stop-server: ## Stop Server
	docker compose down

migrate: ## Run the migrate inside the container
	docker compose run --rm api python manage.py migrate && \
		docker compose run --rm admin python manage.py migrate

makemigrations: ## Run the makemigrations inside the container
	docker compose run --rm api python manage.py makemigrations && \
		docker compose run --rm admin python manage.py makemigrations

shell: ## Run the django shell inside the container
	docker compose run --rm api python manage.py shell

test: ## Run Tests in container
	docker compose run -e "DJANGO_SETTINGS_MODULE=gab_bookstore.settings.api_test" --rm api pytest

superuser: ## Create superuser
	docker compose run --rm admin python manage.py createsuperuser

file_change_owner: ## Change file ownership
	sudo chown ${USER}:${USER} -R .

black: ## Run black on latest changed files, add a HEAD arg to specify the range of commited changes
	black $$(git diff --name-only --diff-filter=ACMR HEAD~$(HEAD) HEAD~0 ':(exclude)*/migrations/*' | grep .py)

black-check: ## Run black but dont affect files
	black $$(git diff --name-only --diff-filter=ACMR HEAD~$(HEAD) HEAD~0 ':(exclude)*/migrations/*' | grep .py) --check

flake8: ## Run flake8 on latest changed files, add a HEAD arg to specify the range of commited changes
	flake8 $$(git diff --name-only --diff-filter=ACMR HEAD~$(HEAD) HEAD~0 ':(exclude)*/migrations/*' | grep .py)

isort: ## Run isort on latest changed files, add a HEAD arg to specify the range of commited changes
	isort $$(git diff --name-only --diff-filter=ACMR HEAD~$(HEAD) HEAD~0 ':(exclude)*/migrations/*' | grep .py)
