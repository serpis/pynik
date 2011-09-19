# -*- coding: utf-8 -*-
import re
import sys
import utility
from json import JSONDecoder
from commands import Command

# TODO:
# - add caching
# - print out error messages
# - rate limiting (only allowed 150 requests per hour to Twitter API)
# - get screen_name from API instead of URL, can be incorrect in URL

class Tweet:
	idno = ''
	user = ''
	text = ''
	erro = ''

def get_tweet_text(idno):
	decoder = JSONDecoder()
	url = "https://api.twitter.com/1/statuses/show/" + idno + ".json"
	response = utility.read_url(url)

	if not response:
		# Couldn't connect to Twitter API
		return False

	try:
		data = decoder.decode(response['data'])
	except Exception:
		# Couldn't parse the API output
		return False

	# Use latin-1 to make IRCClient.send() happy
	return data.get(u"text").encode('latin-1', 'replace')

def get_tweet(message):
	regexp = 'https://twitter.com/#!/(\w+)/status/(\d+)'
	m = re.search(regexp, message, re.IGNORECASE)
	if m:
		tweet = Tweet()
		tweet.user = m.group(1)
		tweet.idno = m.group(2)
		tweet.text = get_tweet_text(tweet.idno)
		if tweet.text:
			return tweet
		else:
			return False
	else:
		return False

class TweetCommand(Command):
	hooks = ['on_privmsg']

	def on_privmsg(self, bot, source, target, message):
		tweet = get_tweet(message)

		if tweet:
			output = "@" + tweet.user + ": " + "\"" + tweet.text + "\""
			bot.tell(target, output)
