# coding: utf-8

pi = "3.141592653589793238462643383279"\
+"50288419716939937510582097494459230"\
+"7816406286208998628034825342117067"

import re
import utility
from commands import Command

def control_pi(argument):
	argument = argument.strip()
	if not argument:
		return "No argument given"
	if argument == "3":
		return "Congratulations, you have the knowledge of a three year old!"
	if len(argument) > 50:
		return "Copypasta is FTL!"
	if argument == pi[:len(argument)]:
		return "Congratulations, you know pi to %s decimals" % (len(argument)-2,)
	return "No no, %s isn't pi, try again, truncate this time." % argument

class picomp(Command):
	def __init__(self):
		pass
	
	def trig_pi(self, bot, source, target, trigger, argument):
		return control_pi(argument)
