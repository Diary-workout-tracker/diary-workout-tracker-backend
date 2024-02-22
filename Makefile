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
	make clear-volumes start-containers migrate collectstatic createsuperuser

project-start: # Запустить проект
	make start-containers

project-stop: # Остановить проект
	docker compose -f docker-compose.yml down;
