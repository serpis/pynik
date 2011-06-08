# coding: utf-8 
import re
import pytz

from commands import Command 
from datetime import datetime

def instruction():
	return "Usage: \".timezone (<date> )<time>( <timezone>)( in <timezone>)\", <time>/<date> is written in the specified timezone or Europe/Stockholm as default. If no date is provided today is assumed." 
 
class TimezoneCommand(Command): 
	def __init__(self): 
		pass 
	
	def trig_tz(self, bot, source, target, trigger, argument):
		return self.trig_timezone(bot, source, target, trigger, argument)

	def trig_timezone(self, bot, source, target, trigger, argument):
		""" Converts time (with date) from timezone into another timezone. Summertime should work if date is specified. If no date is specified the current date is assumed. """

		parsed_argument = re.match("([0-9:\- \/]*)\s(.*)", argument)
		if not parsed_argument:
			return "Does not match format.."
		#print parsed_argument.groups()

		formats = [("%Y-%m-%d %H:%M", ""),
			   ("%y-%m-%d %H:%M", ""),
			   ("%d/%m %H:%M", "noyear"),
			   ("%H:%M", "nodate"),
			   ]
		dt = None
		for format in formats:
			try:
				dt = datetime.strptime(parsed_argument.group(1).strip(), format[0])
				dtMatch = format[1]
			except ValueError, e:
				if e.message.find("not match format") != -1:
					continue
				elif e.message.find("unconverted data remains") != -1:
					print "partly matched", format[0], e
				else:
					raise
		if dt is None:
			return "Unable to parse datetime with: " + ", ".join(map(lambda x: x[0], formats))

		now = datetime.now()
		if dtMatch == "nodate":
			dt = datetime(now.year, now.month, now.day, dt.hour, dt.minute)
		elif dtMatch == "noyear":
			dt = datetime(now.year, dt.month, dt.day, dt.hour, dt.minute)

		#print "Got dt!", dt

		def itz(t):
			replaces = [ (["est", "edt"], "US/Eastern"),
				     (["cst", "cdt"], "US/Central"),
				     (["mst", "mdt"], "US/Mountain"),
				     (["pst", "pdt"], "US/Pacific"),
				     ]

			for replace in replaces:
				if t.lower() in replace[0]:
					t = replace[1]

			return pytz.all_timezones[map(lambda x: x.lower(), pytz.all_timezones).index(t.lower())]

		# Parse timezones
		cmds = parsed_argument.group(2).split(" ")
		tzFrom = pytz.timezone("Europe/Stockholm")
		tzTo = pytz.timezone("Europe/Stockholm")
		if cmds[0] == "in":
			tzTo = pytz.timezone(itz(cmds[1]))
		else:
			tzFrom = pytz.timezone(itz(cmds[0]))
			if len(cmds) == 3 and cmds[1] == "in":
				tzTo = pytz.timezone(itz(cmds[2]))
		
		convertedDt = tzFrom.localize(dt).astimezone(tzTo)
		dt = tzFrom.localize(dt).astimezone(tzFrom)
		#print str(convertedDt)
		return str(dt) + " " + str(tzFrom) + " is " + str(convertedDt) + " " + str(tzTo)

# Unittest
import unittest
class TestTimezonePlugin(unittest.TestCase):
	def setUp(self):
		# Mock now()
		class datetime:
			@staticmethod
			def now():
				return realdatetime(2011, 6, 8, 12, 34, 00, 155129)
		
	def test1234GmtInCet(self):
		self.assertEqual("2011-06-08 12:34:00+00:00 GMT is 2011-06-08 14:34:00+02:00 CET", 
				 TimezoneCommand().trig_tz(None, "", "", "", "12:34 gmt in cet"))

	def test1234InEdt(self):
		self.assertEqual("2011-06-08 12:34:00+02:00 Europe/Stockholm is 2011-06-08 06:34:00-04:00 US/Eastern",
				 TimezoneCommand().trig_tz(None, "", "", "", "12:34 in edt"))

	def test1234Edt(self):
		self.assertEqual("2011-06-08 12:34:00-04:00 US/Eastern is 2011-06-08 18:34:00+02:00 Europe/Stockholm",
				 TimezoneCommand().trig_tz(None, "", "", "", "12:34 edt"))

	def test1234EdtInGmt(self):
		self.assertEqual("2011-06-08 12:34:00-04:00 US/Eastern is 2011-06-08 16:34:00+00:00 GMT", 
				 TimezoneCommand().trig_tz(None, "", "", "", "12:34 edt in gmt"))

	def test7pmEdtInCet(self):
		self.assertEqual("2011-06-08 19:00:00-04:00 US/Eastern is 2011-06-09 01:00:00+02:00 CET",
				 TimezoneCommand().trig_tz(None, "", "", "", "7pm edt in cet"))

	def test20100505_1234EdtInCet(self):
		self.assertEqual("2010-05-05 12:34:00-04:00 US/Eastern is 2010-05-05 18:34:00+02:00 CET",
				 TimezoneCommand().trig_tz(None, "", "", "", "2010-05-05 12:34 edt in cet"))

	def testUnixTime(self):
		self.assertEqual("1307536440+02:00 Europe/Stockholm is 2010-05-05 12:34:00+02:00 Europe/Stockholm",
				 TimezoneCommand().trig_tz(None, "", "", "", "1307536440"))

	def testUnixTime(self):
		self.assertEqual("1307536440+00:00 GMT is 2010-05-05 14:34:00+02:00 Europe/Stockholm",
				 TimezoneCommand().trig_tz(None, "", "", "", "1307536440 gmt"))

if __name__ == "__main__":
	unittest.main()

