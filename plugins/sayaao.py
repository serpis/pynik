# coding: utf-8
from commands import Command
class SayAAOCommand(Command):
	
	def trig_sayaao(self, bot, source, target, trigger, argument, network):
		bot.tell(network, target, u"Detta är åäö i UTF-8".encode("UTF-8"))
		bot.tell(network, target, u"och detta är åäö i ISO-8859-1".encode("ISO-8859-1"))
		return None
