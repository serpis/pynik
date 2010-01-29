# coding: utf-8

from commands import Command
import random

class Magic8Ball(Command):
	def trig_8ball(self, bot, source, target, trigger, argument):
		if len(argument) < 5:
			return "I don't think that is a question"
		elif argument.lower().find("ice") != -1:
			return "Ask again later"
		else:
			answers = ["As I see it, yes", "It is certain", "It is decidedly so", "Most likely", "Outlook good", "Signs point to yes", "Without a doubt", "Yes", "Yes - definitely", "You may rely on it", "Reply hazy, try again", "Ask again later", "Better not tell you now", "Cannot predict now", "Concentrate and ask again", "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful", "It could happen!"]		

			return random.choice(answers)
