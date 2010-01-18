# coding: utf-8

from commands import Command
import re
import utility

class TVCommand(Command):
	def extract_channel_info(self, contents, channel_name):
		m = re.search('(<div class="kanalRubrik">' + channel_name + '.*?<\/div><\/div>)', contents)
		if m:
			contents = m.group(1)
			
			m = re.search('<div class="kanalRubrik">' + channel_name + '<\/div>.*?<img src="img\/.*?_orange.gif" alt="" title="(.*?)"\/><\/div> (.*?) <a href="#" class="prgm_orange"', contents)
			if m:
				show_name = m.group(1)
				show_start = m.group(2)
				show_end = ''
				show_movie = ''

				m = re.search('<div class="kanalRubrik">' + channel_name + '<\/div>.*?<img src="img\/(.*?)_orange.gif" alt="" title=".*?"\/>.*?<img src="img\/.*?_yellow.gif" alt="" title=".*?"\/><\/div> (.*?) <a href="#" class="prgm_yellow"', contents)

				if m:
					#show_movie = ' MOVIE' if m.group(1) == 'mov'
					show_end = m.group(2)

				show_name = show_name.replace('&aring;', 'å').replace('&auml;', 'ä').replace('&ouml;', 'ö')
				show_name = show_name.replace('&Aring;', 'Å').replace('&Auml;', 'Ä').replace('&Ouml;', 'Ö')
				show_name = show_name.replace('&amp;', '&')

				show_start = show_start.replace(':', '')
				show_end = show_end.replace(':', '')

				s = "%s-%s %s%s" % (show_start, show_end, show_name, show_movie)

				return s
		return None
	
	def trig_tv(self, bot, source, target, trigger, argument):
		response = utility.read_url("http://www.tv.nu/")
		data = response["data"]

		if len(argument):
			channel = argument
			
			s = self.extract_channel_info(data, channel)
			if s:
				return "Currently on %s: %s." % (channel, s)
			else:
				return "Could not find that channel. Try http://tvguide.swedb.se/tv?=NU"
		else:
			channels = ['SVT 1', 'SVT 2', 'TV3', 'TV4', 'TV4+', 'Kanal 5', 'TV6', 'Discovery Mix', 'MTV']
			descriptions = []

			for channel in channels:
				s = self.extract_channel_info(data, channel)
				if s:
					descriptions.append(channel + ': ' + s)
			descriptions.append('http://tvguide.swedb.se/tv?=NU')

			return " | ".join(descriptions)
