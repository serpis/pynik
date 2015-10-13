# coding: utf-8

import sys
import re
import datetime
import utility
import tweet
from plugins import Plugin
from commands import Command
import command_catcher

class URL():
	url = ''
	title = ''
	timestamp = ''
	nick = ''
	def is_match(self, searchword):
		if self.url and re.search(searchword, self.url, re.IGNORECASE):
			return True
		if self.title and re.search(searchword, self.title, re.IGNORECASE):
			return True
		if self.nick and re.search(searchword, self.nick, re.IGNORECASE):
			return True
		return False


def get_title(url):
	import urllib
	if not re.search('[^:]+:\/\/', url):
		url = 'http://' + url

	response = utility.read_url(url)
	if response == None:
		return None
	
	data = response["data"]
	data = data.replace("\r", "").replace("\n", "")

	m = re.search('<title[^>]*>\s*(.+?)\s*<\/title>', data, re.IGNORECASE|re.MULTILINE)

	if m:
		title = m.group(1)
		title = re.sub('\s+', ' ', title)
		return utility.unescape(re.sub('<.+?>', '', title))
	else:
		return None


class TitleReaderPlugin(Command):
	hooks = ['on_privmsg']
	urls = {}
	url_list = []
	url_masks = {}

	# dict of channel to timestamp
	# used to turn off title announcement for one url
	no_spoil_dict = {}

	def __init__(self):
		pass


	def on_privmsg(self, bot, source, target, message):
		m = re.search('((https?:\/\/|www\.)\S+)', message, re.IGNORECASE)

		if m:
			url = m.group(1)
			self.urls[target] = URL()
			self.urls[target].url = m.group(1)
			self.urls[target].nick = source
			self.urls[target].timestamp = 'test'
			tweetbool = tweet.match_tweet_url(url)
			try:
				title = utility.timeout(get_title, 10, (url,))
				self.urls[target].title = title
				self.save_last_url(target)
				if not tweetbool and target in ['#c++.se', '#d1d', '#lithen', "#d2006","#testchannel"]:
					# don't announce title if we've been asked to be quiet
					spoiler_averted = False
					if target in self.no_spoil_dict:
						ts = self.no_spoil_dict[target]
						del self.no_spoil_dict[target]
						now = datetime.datetime.now()
						diff_secs = (now - ts).total_seconds()
						if diff_secs < 60:
							spoiler_averted = True
					if not spoiler_averted:
						bot.tell(target, self.clean(url, title))
			except utility.TimeoutException:
				pass

	def trig_nospoiler(self, bot, source, target, trigger, argument):
		self.no_spoil_dict[target] = datetime.datetime.now()
		return "ok ok I'll be quiet XD"

	def save_last_url(self, target):
		self.url_list.append(self.urls[target])
		self.save_urls()


	def trig_urlsearch(self, bot, source, target, trigger, argument):
		resultlist = []
		match = False

		if len(argument) > 0:
			searchlist = argument.split(' ')

			for object in self.url_list:
				match = True
				for word in searchlist:
					if not object.is_match(word):
						match = False
						break
				if match:
					resultlist.append(object)

			if len(resultlist) > 0:
				if resultlist[-1].title:
					title = resultlist[-1].title
				else:
					title = 'N/A'
				return 'Match 1 of ' + str(len(resultlist)) + ': ' + resultlist[-1].url + ' - ' + title
			else:
				return 'No match found.'
		else:
			return 'Usage: .urlsearch <search string>'


	def trig_title(self, bot, source, target, trigger, argument):
		url = argument.strip()
		
		if not url:
			if target not in self.urls.keys():
				return 'I haven\'t seen any urls here yet.'
			
			url = self.urls[target].url
			title = self.urls[target].title
			
		else:
			title = get_title(argument)
		
		if not title:
			return 'I can\'t find a title for ' + url
		else:
			return self.clean(url, title)


	def save_urls(self):
		utility.save_data("urls", self.url_list)


	def load_urls(self):
		self.url_list = utility.load_data("urls", [])


	def on_load(self):
		self.load_urls()
		self.mask_load()


	def save(self):
		pass


	def on_modified_options(self):
		self.save()


	def clean(self, url, title):
		sitematch = re.match(r'(?:http://|https://|)*(?:www\.)*(.+?)(?:\/.*|$)', url)

		if sitematch != None and sitematch.lastindex >= 1:
			site = sitematch.group(1)
		else:
			return(title)

		if site in self.url_masks.keys():
			result = re.match(self.url_masks[site], title)

			if result != None and result.lastindex >= 1: # we need at least one group
				return result.group(1)
			else:
				return title + " (full title)"

		else:
			# try partial matches. slow as shit, but whaddayagonnado.
			for eSite, eMask in self.url_masks.items():
				match = url.find(eSite)
				if (match != -1):
					return re.search(eMask, title).group(1)
  		return(title)


	def mask_load(self):
		self.url_masks = utility.load_data("urlmasks", {})


	def mask_save(self):
		utility.save_data("urlmasks", self.url_masks)


	def trig_titlemask(self, bot, source, target, trigger, argument):
		sArg = argument.strip()

		m = re.match(r'([^ ]+) *(.*)$', sArg)
		if not m:
			return 'usage: .titlemask <host> <regex> | regex can only have one capturing group'

		site = m.group(1)
		mask = m.group(2)

		if (mask.strip() == ''):
			if site in self.url_masks:
				return 'mask for ' + site + ' is ' + self.url_masks[site]
			else:
				return site + ' has no stored title mask.'
		try:
			compiledMask = re.compile(mask)
		except re.error:
		    return 'invalid regex for ' + site

		if compiledMask.groups < 1:
			return 'Needs exactly one capturing group.'

		if compiledMask.groups > 1:
			return 'Too many capturing groups. Use (?:pattern).'

		site = 	re.match(r'(?:http://|https://|)*(?:www\.)*(.+?)(?:\/.*|$)', site).group(1)
		self.url_masks[site] = mask
		self.mask_save()
		return 'mask '+ mask + ' saved for ' + site


	def trig_reloadtitlemasks(self, bot, source, target, trigger, argument):
		self.mask_load()
		return 'reloaded.'


	def trig_deltitlemask(self, bot, source, target, trigger, argument):
		site = argument.strip()
		if site == '':
			return "You forgot to specify a site. Silly hoo-man."
		if site in self.url_masks:
			del self.url_masks[site]
			self.mask_save()
			return 'mask cleared for ' + site
		else:
			return site + ' not found in title mask database.'

