import os
from pathlib import Path

from django.core.management.base import BaseCommand
from dotenv import load_dotenv
import psycopg2


BASE_DIR = Path(__file__).resolve().parent.parent
path_to_env = os.path.join(BASE_DIR, "..", "infra", ".env")
load_dotenv(path_to_env)


class Command(BaseCommand):
	help = "Creates 100 workouts"

	def handle(self, *args, **kwargs) -> None:
		"Создаёт тестовые тренировки."
		connection = psycopg2.connect(
			host=os.getenv("DB_HOST", default=""),
			database=os.getenv("POSTGRES_DB", default=BASE_DIR / "db.sqlite3"),
			port=os.getenv("DB_PORT", default=5432),
			user=os.getenv("POSTGRES_USER", default="user"),
			password=os.getenv("POSTGRES_PASSWORD", default="password"),
		)
		cursor = connection.cursor()
		for i in range(1, 101):
			insert_records = (
				'INSERT INTO running_day ("day_number", "workout", "workout_info")'
				f'VALUES({i}, \'{{"workout":[{{"duration": {i}, "pace": "бег"}}, '
				f'{{"duration": {i * 2}, "pace": "ходьба"}}]}}\', \'тестовая информация {i}\')'
			)
			cursor.execute(insert_records)

		connection.commit()
		connection.close()
