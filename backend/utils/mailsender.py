from abc import ABC, abstractmethod


class MailSender(ABC):
	@abstractmethod
	def send_code(self, mail: str, code: str):
		pass


class DefaultMailSender(MailSender):
	def send_code(self, mail_address: str, code: str):
		pass
