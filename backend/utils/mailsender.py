from abc import ABC, abstractmethod

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class MailSender(ABC):
	@abstractmethod
	def send_code(self, mail: str, code: str):
		pass


class DefaultMailSender(MailSender):
	def send_code(self, mail_address: str, code: str):
		msg_html = render_to_string(
			"email/new-email.html",
			{
				"code": code,
			},
		)
		msg_plain = strip_tags(msg_html)
		send_mail(
			subject="App code",
			message=msg_plain,
			from_email=settings.EMAIL_HOST_USER,
			recipient_list=[mail_address],
			html_message=msg_html,
			fail_silently=False,
		)
