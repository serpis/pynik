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
	
def sh_url(code):
	return 'http://kdb-5.liu.se/liu/lith/studiehandboken/action.lasso?' + \
		'&-response=svkursplan.lasso' + \
		'&-op=eq&k_budget_year=' + sh_year() + \
		'&-op=eq&k_kurskod=' + code
	
def schedule_url(code, programme):
	url = \
		"http://kdb-5.liu.se/liu/lith/studiehandboken/forlista.lasso?&kod=" + \
		code + "&k_budget_year=" + sh_year()
	if programme:
		url = url + "&-Token.pmk=" + programme
	return url

class LithCourse(Command):
	def __init__(self):
		pass
	
	def trig_lithcourse(self, bot, source, target, trigger, argument):
		argument = argument.strip()
		args = argument.split(' ', 2)
		
		if (not argument) or (len(args) > 2):
			return "Usage: .lithcourse code [programme]"
		
		code = args[0].upper()
		
		if is_valid_course_code(code):
			if (len(args) == 2) and (not re.match("\A[A-Za-z]{1,4}\Z", args[1])):
				return "That doesn't look like a programme :O"
			
			# Fetch the study handbook page for the course
			response = utility.read_url(sh_url(code))
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
			
			# Locate the number of HP credits
			m = re.search(
				"\<span class=\"txtbold\"\>\<b\> (\d{1,2},?\d?) hp\</span\>\</font\>",
				sh_data)
			if m:
				credits = m.group(1).replace(",", ".")
			else:
				credits = "???"
				print "I couldn't find the number of credits for the LiTH course " + \
					code + " O.o"
			
			# Fetch the schedule page for the course from the study handbook
			if len(args) == 1:
				url = schedule_url(code, None)
			else: # Programme parameter given
				url = schedule_url(code, args[1])
			response = utility.read_url(url)
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
					match += block_m[i]
				# Add if not already present
				if match not in schedules:
					schedules.append(match)
			
			# Convert it into a string
			if schedules:
				schedule_text = "Scheduled during " + ", ".join(sorted(schedules))
			else:
				schedule_text = "Not scheduled."
			
			# Combine all the information and return it
			return code + ": " + name + ", " + credits + " HP. " + schedule_text + \
					" | " + sh_url(code)
			
		else:
			return "That doesn't look like a course code :O"

