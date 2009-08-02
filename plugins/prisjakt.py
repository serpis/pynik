# -*- coding: utf-8 -*-

# Plugin created by Merola

import re
import string
import urllib
import utility
from commands import Command

def decode_characters(encoded_string):
	strlen = len(encoded_string)
	decoded_string = ""
	regex = re.compile("\\\\u[0-9a-f]{4}")
	i = 0
	
	while i < (strlen - 5):
		if regex.match(encoded_string[i:i+6]):
			decoded_string += unichr(int(encoded_string[i+2:i+6], 16))
			i += 6
		else:
			decoded_string += encoded_string[i]
			i += 1
	
	if i == (strlen - 5):
		decoded_string += encoded_string[i:strlen]
	
	return decoded_string
	
def prisjakt_search(query_string):
	# Build URLs
	url_product = 'http://www.prisjakt.nu/ajax/jsonajaxserver.php?' + \
			'm=super_search&p={"mode"%3A"' + 'prod_pj' + \
			'"%2C"search"%3A"' + query_string + '"%2C"limit"%3A1%2C"v4"%3A1}'
	url_book = 'http://www.prisjakt.nu/ajax/jsonajaxserver.php?' + \
			'm=super_search&p={"mode"%3A"' + 'bok' + \
			'"%2C"search"%3A"' + query_string + '"%2C"limit"%3A1%2C"v4"%3A1}'

	# Fetch the product result page
	response = utility.read_url(url_product)
	data = response["data"]

	# Look for info
	id_pattern = "\\{'mode': 'produkt', 'produkt_id': '(\\d+)'\\}"
	id_match = re.search(id_pattern, data)

	if not id_match:
		# Fetch the book result page
		response = utility.read_url(url_book)
		data = response["data"]

		# Look for info
		id_pattern = "\\{'mode': 'bok', 'produkt_id': '(\\d+)'\\}"
		id_match = re.search(id_pattern, data)

		url_type = "bok"
	else:
		url_type = "produkt"

	if id_match:
		# We seem to have found something
		product_id = id_match.group(1)

		# Get title
		title_pattern = "class=\\\\\"ikon(14)?\\\\\"( alt=\\\\\"\\\\\")?\\> (.+?) \\\\n"
		encoded_title = re.search(title_pattern, data).group(3)
		# Remove HTML tags
		encoded_title = string.replace(
				encoded_title, '<span class=\\"search_hit\\">', '')
		encoded_title = string.replace(encoded_title, '<\\/span>', '')
		# Decode special characters
		product_title = decode_characters(encoded_title)

		# Get price
		price_pattern = "\\<span class=\\\\\"pris\\\\\"\>(\\d+:-)\\<\\\\\/span\\>"
		product_price = re.search(price_pattern, data).group(1)

		# Done, return info string
		return product_title + ", " + product_price + \
				", http://www.prisjakt.nu/" + url_type + ".php?p=" + product_id + \
				" | All results: http://www.prisjakt.nu/search.php?query=" + query_string
	else:
		return "No product found."

def prisjakt_product(url):
	# Fetch the web page
	response = utility.read_url(url)
	data = response["data"]
	data = data.replace("&nbsp;", "")

	# Look for title
	title_pattern = "\<h1.*?\>(\<a href=\".+?\"\>)?(.+?)(\<\/a\>)?\<\/h1\>"
	title_match = re.search(title_pattern, data)

	if not title_match:
		# Failure
		return "Could not extract product info :("
	
	# Success
	title = utility.unescape(title_match.group(2))
	
	# Look for price
	price_pattern = "&auml;gsta: \<span class=\"pris\">(.|\n)(\d+:-)\<\/span\>"
	price_match = re.search(price_pattern, data)
	price = price_match.group(2)

	# Done, return info string
	return title + ", " + price + ", " + url

class PrisjaktCommand(Command):
	def __init__(self):
		pass
		
	def trig_prisjakt(self, bot, source, target, trigger, argument):
		# Sanitize argument
		argument = argument.strip()
		if not argument:
			return "Usage: .prisjakt <product name> | <product page url>"
		
		if re.match("http:\/\/www\.prisjakt\.nu\/(bok|produkt).php\?\w+=\d+", argument):
			# Parse product page
			return prisjakt_product(argument)
			
		else:
			# Search for products
			
			# We want to use latin1 encoding, i.e. %F6 instead of %C3B6
			argument = urllib.quote_plus(argument, 'åäöÅÄÖ')
			translation = { 'å': '%E5', 'ä': '%E4', 'ö': '%F6', 'Å': '%C5', 'Ä': '%C4', 'Ö': '%D6' }
			for key in translation.keys():
				argument = argument.replace(key, translation[key])
			
			return prisjakt_search(argument)

