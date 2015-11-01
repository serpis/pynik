# coding: utf-8

from commands import Command
import re
import utility

class GoogleSearchCommand(Command):
	def trig_google(self, bot, source, target, trigger, argument):
		url = 'http://www.google.com/search?rls=en&q=' + utility.escape(argument) + '&ie=UTF-8&oe=UTF-8'

		response = utility.read_url(url)

		data = response["data"]

		data = re.sub(r"\n|\r|\r\n", "", data)
		data = re.sub(r" +", " ", data)

		print data

		# try to extract video result
		m = re.search(r'Video results for <em>.*?<\/em>.*?<td valign=top style="padding-right:10px"><a href="(.*?)" class=l.*?>(.*?)</a><br>',data)
		if m:
			text = utility.unescape(m.group(2))
			text = re.sub('<.+?>', '', text)
			link = m.group(1)
			return "%s - %s | %s" % (text, link, url)

		# try to extract calculator result
		#m = re.search('<td><img src="\/images\/icons\/onebox\/calculator-40\.gif" ?width=40 height=40 alt=""><td>&nbsp;<td style="vertical-align:top" >(<h2 class=r( style="font-size:\d+%")?>)?<b>(.*?)<\/b>', data)
		m = re.search('.*?font-size:138%">(.*?)<', data)
		if m:
			answer = m.group(1)
			answer = answer.replace(' &#215;', '×').replace('<sup>', '^')
			answer = re.sub('<.+?>', '', answer)
			return answer

		# try to extract definition
		m = re.search('<img src="\/images\/dictblue\.gif" width=40 height=30 alt=""><td valign=top.*?>(.*?)<br>', data)
		if m:
			definition = utility.unescape(m.group(1))
			definition = re.sub('<.+?>', '', definition)
			return definition

		# try to extract weather
		m = re.search('<b>Weather<\/b> for <b>(.+?)<\/b>.+?<b>(-?\d+).*C<\/b>.+?Current: <b>(.+?)<\/b>', data)

		if m:
			location = m.group(1)
			temperature = m.group(2)
			weather = m.group(3)
			return "%s: %s - %s" % (location, temperature, weather)

		# try to extract time
		m = re.search('alt=""><td valign=middle><b>(.*?)<\/b> .+?day \((.*?)\) - <b>Time</b> in (.*?)<\/table>', data)

		if m:
			time = m.group(1)
			timezone = m.group(2)
			location = m.group(3)
			location = re.sub('<.+?>', '', location)

			return "Time in %s: %s (%s)" % (location, time, timezone)

		# try to extract first hit
		m = re.search('<li class=g><h3 class=r><a href="(.*?)".*?>(.*?)<\/a>(.*?)</div>', data)
		if m:
			text = utility.unescape(m.group(2))
			text = re.sub('<.+?>', '', text)

			link = m.group(1)

			return "%s - %s | %s" % (text, link, url)
		else:
			return url
