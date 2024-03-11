from abc import ABC, abstractmethod

from django.conf import settings
from django.core.mail import send_mail


class MailSender(ABC):
	@abstractmethod
	def send_code(self, mail: str, code: str):
		pass


class DefaultMailSender(MailSender):
	def send_code(self, mail_address: str, code: str):
		send_mail(
			subject="App code",
			message=f"Your code is {code}",
			from_email=settings.EMAIL_HOST_USER,
			recipient_list=[mail_address],
			fail_silently=False,
		)
