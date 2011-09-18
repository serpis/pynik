#-*- coding: iso-8859-1 -*-
import re
import sys
import twitter
from commands import Command

# TODO:
# - add caching

class Tweet:
	idno = ''
	user = ''
	text = ''

def get_tweet_text(idno):
	api = twitter.Api()
	status = api.GetStatus(idno)
	return status.GetText()

def get_tweet(message):
	regexp = 'https://twitter.com/#!/(\w+)/status/(\d+)'
	m = re.search(regexp, message, re.IGNORECASE)
	if m:
		tweet = Tweet()
		tweet.user = m.group(1)
		tweet.idno = m.group(2)
		tweet.text = get_tweet_text(tweet.idno)
		return tweet
	else:
		return False

class CharCommand(Command):
	hooks = ['on_privmsg']

	def on_privmsg(self, bot, source, target, message):
		tweet = get_tweet(message)

		if tweet:
			output = "@" + tweet.user + ": " + "\"" + tweet.text + "\""
			bot.tell(target, output)


# Testing
#arg = sys.argv[1]
twitter_url = "https://twitter.com/#!/gruber/status/115107082008666114"
#tweet_id = get_tweet_id(twitter_url)
#print get_status_text(tweet_id)
