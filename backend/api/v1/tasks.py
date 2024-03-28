from django.conf import settings
from django.core.mail import send_mail

from config.celery import app


@app.task
def send_code(message, recipient_list, html_message):
	"""Отправляет сообщение с кодом."""
	send_mail(
		subject="App code",
		message=message,
		from_email=settings.EMAIL_HOST_USER,
		recipient_list=recipient_list,
		html_message=html_message,
		fail_silently=False,
	)
