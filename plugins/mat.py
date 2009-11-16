# -*- coding: utf-8 -*-

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
		
		# The URL is a bit unclear, possibly this will work
		url = "http://www.cgnordic.com/sv/Eurest-Sverige/Restauranger/Restaurang-Karallen-Linkopings-universitet/Lunchmeny-"
		if (int(datetime.now().strftime("%W"))+1) % 2:
			url += "v-15/"
		else:
			url += "v-13/"
		
		entry_regex = '\<td\>\<strong\>(.+?dag).+?\<\/strong\>\<\/td\>\<\/tr\>(.+?)(?=(\<td\>\<strong\>(.+?dag).+?\<\/strong\>\<\/td\>\<\/tr\>|\<p\>Pris dagens:))'
		entry_day_index = 0
		entry_data_index = 1
		
		dish_regex = '\<\/td\>\s+\<td\>(\s+\<p( align="[a-z]+")?\>)?([^\<]+?)(\<\/p\>)?\<\/td\>\<\/tr\>()'
		dish_name_index = 2
		dish_price_index = 4 # Dummy index.
	
	elif location == "blamesen" or location == "galaxen":
		# Restaurang Blåmesen, Galaxen, LiU
		
		url = "http://davidg.nu/lunch/blamesen.php?price"
		entry_regex = '([A-Za-zåäö]{3,4}dag)(.+?)(?=([A-Za-zåäö]{3,4}dag|$))'
		entry_day_index = 0
		entry_data_index = 1
		
		dish_regex = ': (.+?) \((\d+) kr\)'
		
		dish_name_index = 0
		dish_price_index = 1
		
	elif location == "zenit":
		# Restaurang & Café Zenit, LiU
		url = "http://www.hors.se/restauranger/restaurant_meny.php3?UID=24"
		
		entry_regex = '\<tr\>\<td valign="top" colspan="3"\>\<b\>(.+?dag)\<\/b\>\<\/td\>\<\/tr>(.+?)(\<tr\>\<td colspan="3"\>\<hr\>\<\/td\>\<\/tr\>|Veckans Bistro)'
		entry_day_index = 0
		entry_data_index = 1
		
		# This used to be some clever (?) regex to handle special cases that are
		# possibly not applicable now.
		# \xa4 == ¤
		dish_regex = '(\<td valign="top"\>|\<br \/\>\s*)\xa4 (.+?)(\<br \/\>|\<\/td\>)()'
		dish_name_index = 1
		dish_price_index = 3 # Dummy index.
		
	else:
		return [] # Not implemented yet
	
	# Settings are correct, now it's time to actually do something.
	
	# Fetch the web page
	response = utility.read_url(url)
	data = response["data"]
	data = utility.unescape(data.replace("\n", ""))
	data = data.replace(utility.unescape("&nbsp;"), " ")
	
	#return data
	
	# Build the menu
	menu = []
	for entry in re.findall(entry_regex, data):
		#print entry
		day = entry[entry_day_index]
		dishes = []
		
		for dish in re.findall(dish_regex, entry[entry_data_index]):
			#print dish
			dish_name = dish[dish_name_index].strip()
			dish_name = re.sub('\s+', ' ', dish_name)
			
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
		return "Hittade ingen meny för den platsen/dagen... :("

def liu_food_str(day):
	karallen_menu = food("karallen", day)
	zenit_menu = food("zenit", day)
	blamesen_menu = food("blamesen", day)
	result = ""
	
	if karallen_menu:
		result += "Kårallen: "
		
		stripped_menu = []
		
		for item in karallen_menu[1]:
			dish_string = item.split(" med ", 2)[0]
			dish_string = dish_string.replace("serveras", "").strip().capitalize()
			stripped_menu.append(dish_string)
		
		result += ", ".join(stripped_menu)
	
	if zenit_menu:
		if result:
			result += " | "
		result += "Zenit: "
		
		stripped_menu = []
		
		for item in zenit_menu[1]:
			words = item.split(" ")
			important_words = []
			
			for word in words:
				if word.isupper():
					important_words.append(word.replace(",", "").strip())
			
			# TODO str.capitalize does not work correctly with non-english letters!
			if important_words:
				dish_string = " + ".join(important_words)
				dish_string = dish_string.decode("latin-1").encode("utf-8").capitalize()
				stripped_menu.append(dish_string)
		
		result += ", ".join(stripped_menu)
	
	if blamesen_menu:
		if result:
			result += " | "
		result += "Blåmesen: "
		
		stripped_menu = []
		
		for item in blamesen_menu[1]:
			dish_string = item.split(" m ", 2)[0]
			dish_string = re.sub(' \(\d\d kr\)', '', dish_string).strip().capitalize()
			stripped_menu.append(dish_string)
		
		result += ", ".join(stripped_menu)
	
	if result:
		return result
	else:
		return "Hittade ingen LiU-mat den dagen :("

class MatCommand(Command):
	days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]

	def __init__(self):
		pass
	
	def trig_mat(self, bot, source, target, trigger, argument):
		"""Hämtar dagens (eller en annan dags) meny från vald restaurangs hemsida."""
		
		# Split arguments
		argument = argument.strip()
		args = argument.split(' ', 2)
		
		# Determine location and day
		if (not argument) or (len(args) > 2):
			return "Prova med \".mat plats [dag]\" - de platser jag känner till är: " + \
				"HG, VilleValla, Kårallen, Zenit"
				# TODO automatically generated list?
		elif len(args) == 1:
			day = MatCommand.days[datetime.now().isoweekday()-1].lower()
		else:
			day = args[1].lower()
		location = utility.asciilize(args[0]).lower()
		
		# Do stuff
		if location == "liu":
			return liu_food_str(day)
		else:
			return food_str(location, day)

