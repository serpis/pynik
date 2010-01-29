# -*- coding: utf-8 -*-

# Plugin created by Merola

import re
import string
import utility
from commands import Command

def tyda_lookup(word, lang):
	# Assemble URL
	url = "http://tyda.se/search?w=" + utility.escape(word) + "&source_lang=" + \
		utility.escape(lang)
	
	# Fetch result
	response = utility.read_url(url)
	if response:
		data = response["data"].replace("\n", "")	
	else:
		return "Ohnoes, nothing found."
	
	# Look for word
	pattern = "\<span class=\"tyda_entry_base\"( title=\"[^\"]+\")?\>([^\<]+)\<\/span\>(.*?)\<\/td\>(.+?)\<\/table\>(\<table cellpadding=\"0\" cellspacing=\"0\" class=\"tyda_entry\"\>|\<script type=\"text\/javascript\"\>)"
	match = re.search(pattern, data)
	
	if not match:
		return "No result found, maybe you should try searching manually: " + url
	
	base_word = match.group(2).replace(" (", ", ").replace(")", "")
	inflected_word_data = match.group(3)
	inflected_words = []
	translation_data = match.group(4)
	translated_words = []
	
	pattern = "\<span class=\"tyda_entry_inflected\" title=\"[^\"]+\"\>([^\<]+)\<\/span\>"
	iterator = re.finditer(pattern, inflected_word_data)
	
	for match in iterator:
		inflected_words.append(match.group(1).replace(" (", ", ").replace(")", ""))
	
	if inflected_words:
		inflected_words = " (" + ", ".join(inflected_words) + ")"
	else:
		inflected_words = ""
	
	pattern = "\<a id=\"tyda_transR\d+\" href=\"\/search\/[^\"]+\"\>([^\<]+)\<\/a\>"
	iterator = re.finditer(pattern, translation_data)
	
	for match in iterator:
		translated_words.append(match.group(1))
	
	return base_word + inflected_words + ": " + ", ".join(translated_words) + " | " + url
	
class TydaCommand(Command):
	usage = "Usage: .tyda <word>[, <source language, en or sv>]"
	
	def trig_tyda(self, bot, source, target, trigger, argument):
		"""English-Swedish/Swedish-English dictionary, powered by tyda.se"""
		
		argument = argument.strip()
		args = argument.split(', ', 1)
		
		# Show usage
		if not args[0]:
			return self.usage
			
		# Make sure we have a source language
		if len(args) < 2:
			args.append("ALL")
		
		return tyda_lookup(args[0], args[1])
