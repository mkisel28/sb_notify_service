.PHONY: dev prod down superuser lint mm migrate dump loaddata help

.DEFAULT_GOAL := help

DOCKER_COMPOSE_CMD = docker compose -f docker-compose.yml
DEV_COMPOSE_CMD = $(DOCKER_COMPOSE_CMD) -f docker-compose.dev.yml


ifneq (,$(wildcard .env))
    include .env
    export
endif

dev:
	$(DEV_COMPOSE_CMD) up -d --build

prod:
	$(DOCKER_COMPOSE_CMD) up -d --build

superuser:
	$(DOCKER_COMPOSE_CMD) exec web python src/manage.py createsuperuser

down:
	$(DOCKER_COMPOSE_CMD) down

lint:
	$(DEV_COMPOSE_CMD) exec web black .
	$(DEV_COMPOSE_CMD) exec web ruff check . --fix

mm:
	$(DEV_COMPOSE_CMD) exec web python src/manage.py makemigrations

migrate:
	$(DEV_COMPOSE_CMD) exec web python src/manage.py migrate

dump:
	$(DEV_COMPOSE_CMD) exec web python src/manage.py dumpdata --natural-primary --natural-foreign --indent 2 > src/backup.json

loaddata:
	$(DEV_COMPOSE_CMD) exec web python src/manage.py loaddata src/backup.json

help:
	@echo "Доступные команды:"
	@echo ""
	@echo "  make dev         - Запустить контейнеры в режиме разработки"
	@echo "  make prod        - Запустить контейнеры в продакшен-режиме"
	@echo "  make superuser   - Создать суперпользователя"
	@echo "  make down        - Остановить контейнеры"
	@echo "  make lint        - Проверить и исправить код с помощью Black и Ruff"
	@echo "  make mm          - Создать миграции Django"
	@echo "  make migrate     - Применить миграции Django"
	@echo "  make dump        - Создать резервную копию базы данных в JSON"
	@echo "  make loaddata    - Загрузить данные из дампа JSON"
	@echo "  make help        - Показать этот список команд"

make:
	@$(MAKE) help