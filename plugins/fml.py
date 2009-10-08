# -*- coding: utf-8 -*-

# Plugin created by Merola

import re
import string
import utility
from xml.dom import minidom
from commands import Command

def get_node_text(node):
	text = ""
	
	for child in node.childNodes:
		if child.nodeType == child.TEXT_NODE:
			text += child.data
	
	return text

def get_fml_dom(identifier):
	url = "http://api.betacie.com/view/" + identifier + \
			"/nocomment?key=readonly&language=en"
	response = utility.read_url(url)
	data = response["data"]
	return minidom.parseString(data)

def fml_entry(identifier):
	dom = get_fml_dom(identifier)
	
	if dom.getElementsByTagName("code")[0] == "0":
		return "Today, I could not use the API. FML | http://www.fmylife.com/"
	
	items = dom.getElementsByTagName("items")[0].getElementsByTagName("item")
	
	if not items:
		return "Today, I could not find a result. FML | http://www.fmylife.com/"
	
	item = items[0]
	
	return get_node_text(item.getElementsByTagName("text")[0]) + " | " + \
			"+" + get_node_text(item.getElementsByTagName("agree")[0]) + " / " + \
			"-" + get_node_text(item.getElementsByTagName("deserved")[0]) + \
			" | " + "http://www.fmylife.com/" + \
			get_node_text(item.getElementsByTagName("category")[0]) + "/" + \
			item.getAttribute("id")

class FMLCommand(Command):
	types = ['last', 'random', 'top', 'top_day', 'top_week', 'top_month', 'flop',
			  'flop_day', 'flop_week', 'flop_month', 'love', 'money', 'kids',
			  'work', 'health', 'sex', 'miscellaneous']
	
	usage = "Usage: .fml <type> | .fml <id> | .fml show_types"
	
	def __init__(self):
		pass
		
	def trig_fml(self, bot, source, target, trigger, argument):
		"""Command used to display stories from www.fmylife.com"""
		
		# Sanitize argument
		argument = argument.strip().lower()
		
		if argument:
			m = re.match("http:\/\/www\.fmylife\.com\/\w+\/(\d+)", argument)
			result = ""
			
			# Show all types, if requested
			if argument == 'show_types':
				result = "Available FML types: " + ", ".join(self.types)
			
			# If the argument is a valid type, look it up
			elif (argument in self.types) or (argument.isdigit()):
				result = fml_entry(argument)
			elif m:
				result = fml_entry(m.group(1))
			
			if result:
				# Return result (latin-1 to make IRCClient.send() happy)
				# TODO temporary solution to annoy flindeberg and stop the spam
				bot.tell("flindeberg", result.encode('latin-1', 'replace'))
				return None
		
		# Non-valid argument
		return self.usage
