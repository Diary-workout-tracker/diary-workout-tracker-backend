from abc import ABC, abstractmethod

from django.template.loader import render_to_string
from django.utils.html import strip_tags

from api.v1.tasks import send_code


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
		send_code.delay(msg_plain, [mail_address], msg_html)
