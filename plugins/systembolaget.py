# -*- coding: utf-8 -*-

# Plugin created by Merola

import re
import string
import utility
from commands import Command

def system_status(product_id, store_id):
	# Fetch the web page
	url = "http://systembolaget.se/SokDrycker/Produkt?VaruNr=" + product_id + \
			"&Butik=" + store_id
	response = utility.read_url(url)
	if response:
		data = response["data"].replace("\r", "")
	else:
		return "Ingen produkt med det artikelnumret hittades."
	
	# Look for title
	title_pattern = "class=\"rubrikstor\"\>(.+)\n"
	title_match = re.search(title_pattern, data)

	if not title_match:
		# Failure
		return "Hittade inte produktinfon :("
	
	# Set product info and store name variables
	title_text = title_match.group(1)
	
	origin_pattern = "class=\"text_tabell_rubrik\"\>Land\<\/td\>[\n\s]+\<td class=\"text_tabell\"\>(\<B\>\<A.+?\>)?([\w\s]+)(\<\/A\>\<\/B\>)?\<\/td\>"
	origin_text = re.search(origin_pattern, data).group(2)
	
	percentage_pattern = "class=\"text_tabell_rubrik\"\>Alkoholhalt\<\/td\>[\n\s]+\<td class=\"text_tabell\"\>(.+?)\<\/td\>"
	percentage_text = re.search(percentage_pattern, data).group(1).replace(",", ".")
	
	store_pattern = "\<option selected=\"selected\" value=\"" + store_id + "\"\>(.+?)\<\/option\>"
	store_text = re.search(store_pattern, data).group(1)
	
	# Look for available packaging options for this product
	product_pattern = "\<img src=\"\/images\/button_plus\.gif\" class=\"LaggTillMinaVaror\" " + \
			"align=\"absmiddle\" onMouseover=\"ddrivetip\(\'L.gg till i \<b\>Mina varor\<\/b\>\'\)\" " + \
			"onMouseout=\"hideddrivetip\(\)\" onClick=\"LaggTillEnArtikel\(\'\d+\'\);\"\>" + \
			"(.+?)" + "\<\/td\>\<td class=\"text_tabell\" valign=\"Top\" " + \
			"background=\"\/images\/tab_bg_blueline\.gif\" style=\"padding-top:5px;\"\>" + \
			"([\w\s]+)" + "\<\/td\>\<td class=\"text_tabell\" align=\"Right\" valign=\"Top\" " + \
			"background=\"\/images\/tab_bg_blueline\.gif\" style=\"padding-top:5px;\"\>" + \
			"\((.+?)\)" + "\<\/td\>\<td class=\"text10pxfet\" align=\"Right\" valign=\"Top\" " + \
			"background=\"\/images\/tab_bg_blueline\.gif\" width=\"87\" style=\"padding-top:5px;\"\>" + \
			"(.+?)" + "\<\/td\>\<td class=\"text_tabell\" align=\"Left\" valign=\"Top\" " + \
			"background=\"\/images\/tab_bg_blueline\.gif\" width=\"183\" " + \
			"bgcolor=\"#FFFFFF\" style=\"padding-top:5px;\"\>.*?\<\/td\>" + \
			"\<td class=\"text_tabell\" valign=\"Top\" background=\"\/images\/tab_bg_blueline\.gif\" " + \
			"style=\"padding-top:5px;\"\>" + \
			"\<strong\>Lagersaldo: \<\/strong\>(\d+) st&nbsp;&nbsp;&nbsp;\<strong\>" + \
			"Plats i butiken: \<\/strong\>(.+?)\<\/td\>"
	product_iterator = re.finditer(product_pattern, data)
	product_list = []
	
	for match in product_iterator:
		# An available packaging option has been found, let's calculate the APK value.
		apk_value = float(percentage_text[:-2]) / 100  # He
		apk_value *= float(match.group(2)[:-3])        # V (expected to be in ml)
		apk_value /= float(match.group(4))             # P
		
		# Add it to the list...
		format_string = "%s %s: %s kr (%s kr/l, APK " + str(round(apk_value, 2)) + \
				"), %s st, hylla %s"
		product_list.append(format_string % match.group(1, 2, 4, 3, 5, 6))
	
	if not product_list:
		# No available packaging options found
		product_list.append("Varan finns inte i denna butik.")
		
	# Assemble string
	result_string = "#%s: %s, %s, %s | %s | %s | %s" % \
			(product_id, title_text, origin_text, percentage_text, store_text, " | ".join(product_list), url)
	
	# Unescape things like &nbsp;
	return utility.unescape(result_string)

class SystembolagetCommand(Command):
	usage = "Användning: .system id <artikelnummer>"
	
	def __init__(self):
		pass
		
	def trig_system(self, bot, source, target, trigger, argument):
		"""Information om systembolagets produkter. Mer funktionalitet kommer framöver!"""
		
		argument = argument.strip().lower()
		args = argument.split(' ', 1)
		
		if not args[0]:
			return self.usage
		
		elif args[0] == 'id':
			if (len(args) < 2) or (not args[1].isdigit()):
				return "Du måste ange ett artikelnummer!"
			else:
				return system_status(args[1], str(110)) # TODO: more stores
		
		else:
			return "Mer funktioner kommer framöver! " + self.usage
