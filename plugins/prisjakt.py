# coding: utf-8

# Plugin created by Merola

import re
import utility
from commands import Command

class PrisjaktCommand(Command):
	def __init__(self):
		pass
	
	def trig_prisjakt(self, bot, source, target, trigger, argument):
		# Sanitize argument
		argument = argument.strip()
		if not argument:
			return "Usage: .prisjakt <product name>"
		argument = utility.escape(argument)

		# Build URL
		url = "http://www.prisjakt.nu/search.php?s=" + argument + "&r=1&e=utf8"

		# Fetch the web page
		response = utility.read_url(url)
		data = response["data"]
		data = data.replace("&nbsp;", "")

		# Look for info
		title_pattern = "\<a href=\"\/produkt\.php\?p=(\d+)\"\>(.+?)\<\/a\>\<\/span\>\<\/td\>"
		title_match = re.search(title_pattern, data)

		if title_match:
			# Seems to be a result page
			title = utility.unescape(title_match.group(2))
			product_id = title_match.group(1)

			price_pattern = "rel=\"nofollow\" \>(\d+:-)\<\/a\>\<\/span\>\<\/td\>"
			price_match = re.search(price_pattern, data)
		else:
			# Maybe this is a product page, try to find info again
			title_pattern = "\<h1.+?\>(.+?)\<\/h1\>"
			title_match = re.search(title_pattern, data)

			if not title_match:
				# Nope, maybe it is an empty result page
				return "No product found."
			
			# That seems to be the case, proceed
			title = utility.unescape(title_match.group(1))

			id_pattern = "\<a href=\"\/produkt\.php\?e=(\d+)\"\>\<span class=\"tab_content\"\>"
			id_match = re.search(id_pattern, data)
			product_id = id_match.group(1)
			
			price_pattern = "\<span class=\"pris\"> (\d+:-)\<\/span\>"
			price_match = re.search(price_pattern, data)
		
		price = price_match.group(1)

		# Done, return info string
		return title + ", " + price + ", http://www.prisjakt.nu/produkt.php?p=" + product_id

