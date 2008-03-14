# coding: utf-8

pi = "3.141592653589793238462643383279"\
+"50288419716939937510582097494459230"\
+"7816406286208998628034825342117067"

import re
import utility
from commands import Command
				
class kolli(Command):
	def __init__(self):
		pass
	
	def trig_kolli(self, bot, source, target, trigger, argument):
		argumet = argument.strip()
		if len(argument) > 50:
			return "Copypasta is FTL!"
		if argument == pi[:len(argument)]:
			return "Grattis, du kan pi till %s decimaler" % len(argument)
		return "Nejnej, %s är inte pi, försök igen, trunkera, avrunda inte" % argument
