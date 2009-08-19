# -*- coding: latin-1 -*-

# Plugin created by Merola, heavily based on HGMat

import re
import utility
from commands import Command
from datetime import datetime

def menu(location):
	# Set location-specific settings
	if location == "[hg]" or location == "hg":
		# Ryds Herrgård [hg], Linköping
		url = "http://www.hg.se/?restaurang/kommande"
		
		entry_regex = '\<h2\>(.+?dag)en den .+?\<\/h2\>(.+?)(?=(\<h2\>|\<em\>))'
		entry_day_index = 0
		entry_data_index = 1
		
		dish_regex = '\<p\>(.+?)\<br\>(.+?((\d+?) kr))?'
		dish_name_index = 0
		dish_price_index = 3
	
	elif location == "villevalla" or location == "vvp":
		# VilleValla Pub, Linköping
		url = "http://www.villevallapub.se/"
		
		entry_regex = '\<td valign="top" style="padding-right: 2px;"\>\<strong\>(.+?dag)\<\/strong\>\<\/td\>\s*\<td\>(.+?)\<\/td\>'
		entry_day_index = 0
		entry_data_index = 1
		
		dish_regex = '\A(.+?) ((\d+?) :-)\Z'
		dish_name_index = 0
		dish_price_index = 2
	
	elif location == "karallen" or location == "kara":
		# Restaurang Kårallen, LiU
		url = "http://www.cgnordic.com/sv/Eurest-Sverige/Restauranger/Restaurang-Karallen-Linkopings-universitet/Lunchmeny-v-15/"
		
		entry_regex = '\<td\>\<strong\>(.+?dag).+?\<\/strong\>\<\/td\>\<\/tr\>(.+?)(?=(\<td\>\<strong\>(.+?dag).+?\<\/strong\>\<\/td\>\<\/tr\>|\<p\>Pris dagens:))'
		entry_day_index = 0
		entry_data_index = 1
		
		dish_regex = '\<\/td\>\s+\<td\>(\s+\<p( align="[a-z]+")?\>)?(.+?)(\<\/p\>)?\<\/td\>\<\/tr\>()'
		dish_name_index = 2
		dish_price_index = 4 # Dummy index.
		
	elif location == "vallfarten" or location == "val":
		# Restaurang Vallfarten, LiU
		url = "http://www.fazergroup.com/templates/Fazer_RestaurantMenuPage.aspx?id=5618&epslanguage=SV"
		
		entry_regex = '(\<div class="menufactstext" \>\s+\<p\>|\<p\>\<br \/\>)(.+?dag) (\<br \/\>.+?)\<\/p\>'
		entry_day_index = 1
		entry_data_index = 2
		
		dish_regex = '(?<=\<br \/\>)(.+?) ((\d+?) kr|\Z)'
		dish_name_index = 0
		dish_price_index = 2
		
	elif location == "zenit":
		# Restaurang & Café Zenit, LiU
		url = "http://www.hors.se/restauranger/restaurant_meny.php3?UID=24"
		
		entry_regex = '\<tr\>\<td valign="top" colspan="3"\>\<b\>(.+?dag)\<\/b\>\<\/td\>\<\/tr>(.+?)\<tr\>\<td colspan="3"\>\<hr\>\<\/td\>\<\/tr\>'
		entry_day_index = 0
		entry_data_index = 1
		
		# TODO
		# This is NOT a good solution, since it will generate one empty dish per entry.
		# However, something is needed in order to exclude the always available dishes.
		# Cutting the entry in half at "Pris" in the regex above seems to fail
		# if the restaurant is closed one day (closed days do not contain "Pris")
		# \xa4 == ¤
		dish_regex = '((\<td valign="top"\>|\<br \/\>\s*)\xa4 (.+?)(\<br \/\>|\<\/td\>)()|Pris:.+()()()())'
		dish_name_index = 2
		dish_price_index = 4 # Dummy index.
		
	else:
		return [] # Not implemented yet
	
	# Settings are correct, now it's time to actually do something.
	
	# Fetch the web page
	response = utility.read_url(url)
	data = response["data"]
	data = utility.unescape(data.replace("\n", ""))
	data = data.replace(utility.unescape("&nbsp;"), " ")
	
	# Build the menu
	menu = []
	for entry in re.findall(entry_regex, data):
		#print entry
		day = entry[entry_day_index]
		dishes = []
		
		for dish in re.findall(dish_regex, entry[entry_data_index]):
			#print dish
			dish_name = dish[dish_name_index].strip()
			if not dish_name:
				pass # Odd input or bad regex
			elif dish_name.find(">") != -1:
				print "Hmm, I got an odd dish from " + location + ": " + dish_name
			elif dish[dish_price_index]:
				# Price found, let's add it
				dishes.append(dish_name + " (" + dish[dish_price_index] + " kr)")
			else:
				# No price, exclude it
				dishes.append(dish_name)
		
		menu.append((day, dishes))
	
	# Done!
	return menu

def food(location, day):
	input_day = day

	best_match = None
	best_matching_chars = 0

	for entry in menu(location):
		entry_day = entry[0].lower()

		loop_len = min(len(input_day), len(entry_day))

		matching_chars = 0

		for i in range(loop_len):
			if input_day[i] == entry_day[i]:
				matching_chars += 1		
			else:
				break

		if matching_chars > best_matching_chars:
			best_match = entry
			best_matching_chars = matching_chars

	return best_match

def food_str(location, day):
	day_menu = food(location, day)

	if day_menu:
		return "%s: %s" % (day_menu[0], " | ".join(day_menu[1]))
	else:
		return "Hittade ingen meny för den platsen/dagen... :-("

class MatCommand(Command):
	days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]

	def __init__(self):
		pass
	
	def trig_mat(self, bot, source, target, trigger, argument):
		# Split arguments
		argument = argument.strip()
		args = argument.split(' ', 2)
		
		# Determine location and day
		if (not argument) or (len(args) > 2):
			return "Prova med \".mat plats [dag]\" - de platser jag känner till är: " + \
				"HG, VilleValla, Kårallen, Vallfarten, Zenit"
				# TODO automatically generated list?
		elif len(args) == 1:
			day = MatCommand.days[datetime.now().isoweekday()-1].lower()
		else:
			day = args[1].lower()
		location = utility.asciilize(args[0]).lower()
		
		# Do stuff
		return food_str(location, day)
