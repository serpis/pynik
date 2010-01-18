# coding: utf-8

# plugin created by Merola

import re
import utility
from datetime import datetime
from commands import Command

def is_valid_course_code(code):
	# A valid course code consists of 6 characters, e.g. TATM79, TDP001 or NBIA19
	return re.match("\A([A-Za-z0-9]{6})\Z", code)

def sh_year():
	# TODO: Maybe it would be nice to somehow 'predict' which year we want.
	# For example, info about a Vt course should be retrieved from the SH page for
	# the upcoming year, if the command is run during the Ht.
	return str(datetime.now().year)
	
def sh_url(code, year):
	return 'http://kdb-5.liu.se/liu/lith/studiehandboken/action.lasso?' + \
		'&-response=svkursplan.lasso' + \
		'&-op=eq&k_budget_year=' + year + \
		'&-op=eq&k_kurskod=' + code
	
def schedule_url(code, programme, year):
	url = \
		"http://kdb-5.liu.se/liu/lith/studiehandboken/forlista.lasso?&kod=" + \
		code + "&k_budget_year=" + year
	if programme:
		url += "&-Token.pmk=" + programme
	return url

def lith_course_info(code, programme, year):
	# Fetch the study handbook page for the course
	response = utility.read_url(sh_url(code, year))
	sh_data = response["data"]
	
	# Locate the Swedish course name
	m = re.search(
		"\<span class=\"txtbold\"\>\<b\>(.*?), \d{1,2},?\d? p \</b\>",
		sh_data)
	if m:
		name = utility.unescape(m.group(1))
	else:
		return "Hmm, are you sure the course code is " + code + "?"
	
	# Locate the English course name
	m = re.search(
		"\<br\>/(.*?)/\</b\>\</span\>",
		sh_data)
	if m:
		name = name + " (" + utility.unescape(m.group(1)) + ")"
	else:
		print "I couldn't find the English name of the LiTH course " + \
			code + " O.o"
	
	# Locate the number of HP (ECTS) credits
	m = re.search(
		"\<span class=\"txtbold\"\>\<b\> (\d{1,2},?\d?) hp\</span\>\</font\>",
		sh_data)
	if m:
		credits = m.group(1).replace(",", ".")
	else:
		credits = "???"
		#print "I couldn't find the number of credits for the LiTH course " + \
		#	code + " O.o"
	
	# Locate the advancement level
	m = re.search(
		"\<span class=\"txtkursivlista\"\>Utbildningsniv&aring; \(G1,G2,A\):\<\/span\>\<i\> \<\/i\>\<span class=\"txtlista\"\>(.+?)\<\/span\>",
		sh_data)
	if m:
		level = m.group(1)
	else:
		level = "???"
	
	# Fetch the schedule page for the course from the study handbook
	response = utility.read_url(schedule_url(code, programme, year))
	sh_data = response["data"]
	
	# Match study periods
	# (Usually ([HV]t[12]) but some odd courses have other formats, e.g. Ht2a)
	period_m = re.findall(
		"\<td\>\<span class=\"txtlista\"\>\d([HV]t.*?)\</span\>\</td\>",
		sh_data)
	
	# Match blocks
	# (Usually ([1-4]) but some courses have other formats, e.g. "-", "" or "1+2+4")
	block_m = re.findall(
		"&-Token.ksk=\[Field:'k_kurskod'\]\"\>---\>" + "(.*?)" + \
		"\<!---\<\/a\>---\>\<\/span\>\<\/td\>",
		sh_data)
	
	# Build a list of schedule occasions
	schedules = []
	for i in range(len(period_m)):
		# Assemble an occasion string
		match = period_m[i] + "."
		if not block_m[i]:
			match += "?"
		else:
			match += block_m[i].replace(", ", "+")
		
		# Add if not already present
		if match not in schedules:
			schedules.append(match)
	
	# Convert it into a string
	if schedules:
		schedule_text = "Scheduled during " + ", ".join(sorted(schedules))
	else:
		schedule_text = "Not scheduled " + year + "."
	
	# Combine all the information and return it
	return code + ": " + name + ", " + credits + " HP on level " + level + \
			". " + schedule_text + " | " + sh_url(code, year)

class LithCourse(Command):
	def __init__(self):
		pass
	
	def trig_lithcourse(self, bot, source, target, trigger, argument):
		# Parse parameters...
		argument = argument.strip()
		args = argument.split(' ', 3)
		
		if (not argument) or (len(args) > 3):
			return "Usage: .lithcourse code [year] [programme]"
		
		code = args[0].upper()
		year = None
		programme = None
		
		if not is_valid_course_code(code):
			return "That doesn't look like a course code :O"
		
		if len(args) >= 2:
			if re.match("\A(19|20)\d\d\Z", args[1]):
				year = args[1]
			elif re.match("\A[A-Za-z]{1,4}\Z", args[1]):
					programme = args[1]
			else:
				return "That doesn't look like a year or programme :O"
		if len(args) == 3:
			if re.match("\A[A-Za-z]{1,4}\Z", args[2]):
				if programme:
					return "Two programmes at once? :S"
				else:
					programme = args[2]
			elif re.match("\A(19|20)\d\d\Z", args[2]):
				if year:
					return "Two years at once? :S"
				else:
					year = args[2]
			else:
				return "That doesn't look like a year or programme :O"
		
		if not year:
			year = sh_year()
		
		return lith_course_info(code, programme, year)

