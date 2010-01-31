# coding: utf-8

import os
import re
import datetime
from commands import Command
from xml.dom import minidom
import utility
import urllib
import time

class Reminder:
	def __init__(self, nick, trigger_time, message):
		self.nick = nick
		self.trigger_time = trigger_time
		self.message = message

class ReminderCommand(Command):

	reminders = []

	def __init__(self):
		self.next_beat = None

	def trig_reminder(self, bot, source, target, trigger, argument):
		m = re.search('(\d\d?):(\d\d) (.+)', argument)

		if m:
			hour, minute, message = m.groups()

			print hour, minute, message

			now = datetime.datetime.today()
			trigger_time = datetime.datetime(now.year, now.month, now.day, int(hour), int(minute))
			if trigger_time < now:
				trigger_time += datetime.timedelta(1)
			
			self.reminders.append(Reminder(source, trigger_time, message))

			self.save()

			until_then = trigger_time - now

			return "The reminder was successfully added. I will message you in roughly %s hours and %s minutes." % (until_then.seconds / 3600, until_then.seconds % 3600 / 60)
		else:
			return "Usage: reminder <hour>:<minute> <message>."

	def trig_reminders(self, bot, source, target, trigger, argument):
		reminders = []
		for reminder in self.reminders:
			if reminder.nick == source:
				reminders.append(reminder)

		if reminders:
			reminders = map(lambda r: "%s:%s %s" % (r.trigger_time.hour, r.trigger_time        .minute, r.message), reminders)
			return " | ".join(reminders)
		else:
			return "You have no reminders."

	def timer_beat(self, bot, now):
		if not self.next_beat or self.next_beat < now:
			self.next_beat = now + datetime.timedelta(0, 0, 0, 0, 1)

			to_remove = []

			for reminder in self.reminders:
				if reminder.trigger_time <= now:
					bot.tell(reminder.nick, "Beep beep! %s" % reminder.message)
					to_remove.append(reminder)

			if to_remove:
				for reminder in to_remove:
					self.reminders.remove(reminder)

				self.save()

	def save(self):
		utility.save_data("reminders", self.reminders)

	def on_load(self):
		self.reminders = utility.load_data("reminders", [])
	
	def on_unload(self):
		self.reminders = []
