from django.db import models


class MotivationalPhrase(models.Model):
	text = models.TextField()

	def __str__(self):
		return self.text


class RecreationPhrase(models.Model):
	text = models.TextField()

	def __str__(self):
		return self.text
