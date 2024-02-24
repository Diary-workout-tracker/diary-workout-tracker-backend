from abc import ABC, abstractmethod


class MailSender(ABC):
	@abstractmethod
	def send_mail(self, mail: str, code: str):
		pass
