# Команды для prod
clear-volumes-prod: # Удаление Volumes
	docker compose -f docker-compose.production.yml down --volumes

start-containers-prod: # Запуск контейнеров
	docker compose -f docker-compose.production.yml up -d;
	@sleep 3;

migrate-prod: # Выполнить миграции Django
	docker compose exec backend poetry run python manage.py migrate

collectstatic-prod: # Собрать статику Django
	docker compose exec backend poetry run python manage.py collectstatic --noinput
	docker compose exec backend cp -r /app/static/. /backend_static/static/

createsuperuser-prod: # Создать супер пользователя
	docker compose exec backend poetry run python manage.py createsuperuser --noinput

project-init-prod: # Инициализировать проект
	make clear-volumes-prod start-containers-prod migrate-prod collectstatic-prod createsuperuser-prod

project-start-prod: # Запустить проект
	make start-containers

project-stop-prod: # Остановить проект
	docker compose -f docker-compose.yml down;


# Команды для dev
clear-volumes-dev: # Удаление Volumes
	docker compose -f docker-compose.dev.yml --env-file ./infra/.env down --volumes

start-containers-dev: # Запуск контейнеров
	docker compose -f docker-compose.dev.yml --env-file ./infra/.env up -d;
	@sleep 3;

start-server-dev: # Запуск сервера
	poetry run python backend/manage.py runserver

migrate-dev: # Выполнить миграции Django
	poetry run python backend/manage.py migrate

collectstatic-dev: # Собрать статику Django
	poetry run python backend/manage.py collectstatic --noinput

createsuperuser-dev: # Создать супер пользователя
	poetry run python backend/manage.py createsuperuser --noinput

project-init-dev: # Инициализировать проект
	make clear-volumes-dev start-containers-dev migrate-dev collectstatic-dev createsuperuser-dev start-server-dev

project-start-dev: # Запустить проект
	make start-containers start-server-dev

containers-stop-dev: # Остановить контейнеры
	docker compose -f docker-compose.dev.yml  --env-file ./infra/.env down;
