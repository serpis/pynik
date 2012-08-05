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

# called in plugins/title_reader.py
def match_tweet_url(url):
	regexp = '(http|https)://twitter.com/((#!/(\w+))|(\w+))/(status|statuses)/(\d+)'
	m = re.search(regexp, url, re.IGNORECASE)
	return m

def get_tweet_text_and_user(tweet):
	decoder = JSONDecoder()
	url = "https://api.twitter.com/1/statuses/show/" + tweet.idno + ".json"
	response = utility.read_url(url)

	if not response:
		# Couldn't connect to Twitter API
		return False

	try:
		data = decoder.decode(response['data'])
	except Exception:
		# Couldn't parse the API output
		print("Couldn't parse the API output")
		return False

	# Use latin-1 to make IRCClient.send() happy
	tweet.text = data.get(u"text").encode('latin-1', 'replace').replace('\n', ' ')
	tweet.user = data.get(u"user").get(u"screen_name").encode('latin-1', 'replace')
	return tweet

def get_tweet(message):
	m = match_tweet_url(message)
	if m:
		tweet = Tweet()
		tweet.idno = m.group(6)
		tweet = get_tweet_text_and_user(tweet)
		if tweet:
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
			output = "@" + tweet.user + ": " + tweet.text
			bot.tell(target, output)
