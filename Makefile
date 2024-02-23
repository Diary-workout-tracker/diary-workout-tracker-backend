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
clear-volumes: # Удаление Volumes
	docker compose -f docker-compose.yml down --volumes

start-containers: # Запуск контейнеров
	docker compose -f docker-compose.yml up -d;
	@sleep 3;

migrate: # Выполнить миграции Django
	docker compose exec backend poetry run python manage.py migrate

collectstatic: # Собрать статику Django
	docker compose exec backend poetry run python manage.py collectstatic --noinput
	docker compose exec backend cp -r /app/static/. /backend_static/static/

createsuperuser: # Создать супер пользователя
	docker compose exec backend poetry run python manage.py createsuperuser --noinput

project-init: # Инициализировать проект
	make clear-volumes-prod start-containers-prod migrate-prod collectstatic-prod createsuperuser-prod

project-start: # Запустить проект
	make start-containers

project-stop: # Остановить проект
	docker compose -f docker-compose.yml down;
