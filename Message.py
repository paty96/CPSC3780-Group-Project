import datetime

class Message:
	def __init__(self, time, sender, text):
		self.message_time = time
		self.message_from = sender
		self.message_text = text