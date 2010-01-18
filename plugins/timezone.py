# coding: utf-8 
 
from commands import Command 
 
timezone = ['GMT', 'UT', 'UTC', 'WET', 'CET', 'EET', 'BT', 'CCT', 'JST', 'GST', 'IDLE', 'NZST', 'WAT', 'AT', 'AST', 'EST', 'CST', 'MST', 'PST', 'YST', 'AHST',  'CAT',  'HST',  'NT', 'IDLW'] 
timeoffsets = [0, 0, 0, 0, 1, 2, 3, 8, 9, 10, 12, 12, -1, -2, -4, -5, -6, -7, -8, -9, -10, -10, -10, -11, -12] 
defaultzone = 4 
			 
def instructions(): 
	return "Usage: \".timezone <time>( <timezone>)( in <timezone>)\" or \".timezone <timezone>\", <time> is written as \"hour(:minute)( am/pm)\", for a list of timezones see .timezones" 
 
class TimezoneCommand(Command): 
	def __init__(self): 
		pass 
 
	def trig_timezones(self, bot, source, target, trigger, argument): 
		return ', '.join(timezone) 
 
	def trig_timezone(self, bot, source, target, trigger, argument): 
		parts = argument.split(' in ') 
		 
		usingminutes = False 
		minutes = 0 
		 
		if(len(parts) == 1): 
			split = parts[0].strip().split(' ') 
			 
			if(len(split) == 1): 
				import time 
				minutes = time.gmtime(time.time()).tm_min 
				time = time.gmtime(time.time()).tm_hour + timeoffsets[defaultzone] 
				fromzone = defaultzone 
				using24h = True 
				usingminutes = True 
				gettime = False 
			elif(len(split) == 2): 
				using24h = True 
				gettime = True 
			elif(len(split) == 3):   
				using24h = False 
				gettime = True 
				ispm = (split[1].lower().find('pm') != -1) 
			else: 
				return instructions() 
			 
		elif(len(parts) == 2): 
			gettime = True 
			split = parts[0].strip().split(' ') 
		else: 
			return instructions() 
			 
		if(gettime): 
			fromzone = -1 
			for i in range(len(timezone)): 
				if(split[len(split) -1].strip().upper() == timezone[i]): 
					fromzone = i 
					 
			if(fromzone == -1): 
				fromzone = defaultzone 
 
				if(len(split) == 1): 
					using24h = True 
				elif(len(split) == 2): 
					using24h = False 
					 
					if(split[1].lower().find('pm') != -1): 
						ispm = True 
					elif(split[1].lower().find('am') != -1): 
						ispm = False 
					else: 
						return instructions() 
				else: 
					return instructions() 
			else: 
				if(len(split) == 2): 
					using24h = True 
				elif(len(split) == 3): 
					using24h = False 
					ispm = (split[1].lower().find('pm') != -1) 
				else: 
					return instructions() 
			 
			try: 
				time = int(split[0]) 
			except ValueError: 
				try: 
					t = split[0].split(':') 
					time = int(t[0]) 
					 
					if(len(t) >= 2): 
						minutes = int(t[1]) 
						usingminutes = True 
					 
				except ValueError: 
					return instructions() 
			 
			if(not using24h): 
				if(time == 12): 
					time -= 12 
				if(ispm): 
					time += 12 
			 
			 
		if(time > 24 or time < 0 or minutes > 59 or minutes < 0): 
			return instructions() 
			 
		tozone = -1 
		for i in range(len(timezone)): 
			if(parts[len(parts) -1].strip().upper() == timezone[i]): 
				tozone = i 
				 
		if(tozone == -1): 
			tozone = defaultzone 
			 
			if(gettime == False): 
				return instructions() 
		 
		diff = timeoffsets[tozone] - timeoffsets[fromzone] 
		totime = (time + diff) % 24 
		 
		fromtimestr = mktimestr(time, using24h, usingminutes, minutes) 
		using24h = True 
		usingminutes = True 
		totimestr = mktimestr(totime, using24h, usingminutes, minutes) 
		 
		if(diff == 0): 
			return fromtimestr + " " + timezone[fromzone] 
		elif(diff == 1): 
			diffstr = "(+1 hour)" 
		elif(diff == -1): 
			diffstr = "(-1 hour)" 
		elif(diff > 0): 
			diffstr = "(+" + str(diff) + " hours)" 
		else: 
			diffstr = "(" + str(diff) + " hours)" 
			 
		return fromtimestr + " " + timezone[fromzone] + " is " + totimestr + " " + timezone[tozone] + " " + diffstr 
			 
			 
def mktimestr(time, using24h, usingminutes, minutes): 
	if(not using24h): 
		if(time < 12): 
			tmp = " am" 
		else: 
			time -= 12 
			tmp = " pm" 
		 
		if(time == 0): 
			time = 12 
	else: 
		tmp = "" 
	 
	if(not usingminutes): 
		timestr = str(time) + tmp 
	elif(minutes < 10): 
		timestr = str(time) + ":0" + str(minutes) + tmp 
	else: 
		timestr = str(time) + ":" + str(minutes) + tmp 
		 
	return timestr
