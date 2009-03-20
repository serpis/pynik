# coding: latin-1

import re
import utility
from commands import Command
from datetime import datetime

def hg_menu():
	#url = "http://www.hg.se/kommande_meny.php"
	url = "http://www.hg.se/?restaurang/kommande"
	response = utility.read_url(url)
	data = response["data"]

	data = utility.unescape(data.replace("\n", ""))

	menu = []
	for entry in re.findall('<p class="(even|odd)"><b>(.*?)<\/b><br \/>(.*?)<\/p>', data):
		day = entry[1]
		dishes = []
		for dish in re.findall('(?!<br \/>)(.*?)\t?<br \/>', entry[2]):
			dishes.append(dish)
		
		menu.append((day, dishes))
	return menu

def hg_food(day):
	input_day = day.lower()

	best_match = None
	best_matching_chars = 0

	for entry in hg_menu():
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

def hg_food_str(day):
	day_menu = hg_food(day)

	if day_menu:
		return "%s: %s" % (day_menu[0], ", ".join(day_menu[1]))
	else:
		return "Hittade ingen meny för den dagen... :-("

class HGMatCommand(Command):
	days = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]

	def __init__(self):
		pass
	
	def trig_hgmat(self, bot, source, target, trigger, argument):
		day = None
		if argument:
			day = argument
		else:
			day = HGMatCommand.days[datetime.now().isoweekday()-1]
	
		return hg_food_str(day)
