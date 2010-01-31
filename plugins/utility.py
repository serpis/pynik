# coding: utf-8

from __future__ import with_statement
import pickle
import sys
from plugins import Plugin
import htmlentitydefs
import re
import os
import signal
import string
import settings

class TimeoutException(Exception):
	pass

##
# Removes HTML or XML character references and entities from a text string.
# From: http://effbot.org/zone/re-sub.htm#unescape-html
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def escape(str):
	import urllib
	t = {
		'%E5': '\xe5',
		'%E4': '\xe4',
		'%F6': '\xf6',
		'%C5': '\xc5',
		'%C4': '\xc4',
		'%D6': '\xd6'
	}

	s = urllib.quote_plus(str)

	for key in t.keys():
		s = s.replace(key, t[key])

	return s

latin1_aao_trans = string.maketrans("\xe5\xe4\xf6\xc5\xc4\xd6", "aaoAAO")
utf8_aao_dict = { "å": "a", "ä": "a", "ö": "o", "Å": "A", "Ä": "A", "Ö": "O" }

def asciilize(aaostr):
	source = aaostr.translate(latin1_aao_trans)
	to = ""
	while source:
		if source[0:2] in utf8_aao_dict:
			to += utf8_aao_dict[source[0:2]]
			source = source[2:]
		else:
			to += source[0]
			source = source[1:]

	return to
	
def get_all_subclasses(c):
	l = [c]
	for subclass in c.__subclasses__():
		l.extend(get_all_subclasses(subclass))
	return l

def timeout(f, timeout = 1, args = (), kwargs = {}):
	def handler(signum, frame):
		raise TimeoutException
    
	old = signal.signal(signal.SIGALRM, handler)
	signal.alarm(timeout)

	result = None
	try:
		result = f(*args, **kwargs)
	except:
		signal.alarm(0)
		raise
	finally:
		signal.signal(signal.SIGALRM, old)
	signal.alarm(0)
	return result

def extract_nick(host):
	m = re.search('^(.+)!', host)
	if m:
		return m.group(1)
	else:
		return host

def read_url(url):
	import httpget
	import socket
	
	# THIS AFFECTS SOCKETS GLOBALLY AND SHOULD _NOT_ BE USED!!!
	timeout_time = socket.getdefaulttimeout()
	socket.setdefaulttimeout(15)

	data = httpget.read_url(url)
		
	# THIS AFFECTS SOCKETS GLOBALLY AND SHOULD _NOT_ BE USED!!!
	socket.setdefaulttimeout(timeout_time)

	return data

def save_data(name, data):
	handle = open(os.path.join('data', name + '.txt'), 'w')
	p = pickle.Pickler(handle)
	p.dump(data)
	handle.close()

def load_data(name, default_value=None):
	try:
		with open(os.path.join('data', name + '.txt'), 'r') as handle:
			return pickle.Unpickler(handle).load()
	except:
		print "Could not load data from file 'data/" + str(name) + ".txt' :("
		return default_value

# FIXME use bot.settings/rebuild authentication
def has_admin_privileges(source, target):
	return source in settings.Settings().admin_adminnicks 

nbsp_latin1 = unescape("&nbsp;").encode("latin-1")
nbsp_utf8 = unescape("&nbsp;").encode("utf-8")

def currency_conversion(amount, source, target):
	url = 'http://www.google.com/search?rls=en&q=' + str(amount) + '+' + source + '+in+' + target + '&ie=UTF-8&oe=UTF-8'
	response = read_url(url)
	data = response["data"]
	data = data.replace(nbsp_utf8, "") # Get rid of UTF-8 NBSP
	
	m = re.search('\<b\>\d+(\.\d+)? [^=]+ = (\d+(\.\d+)?)[^\<]+\<\/b\>', data)
	if m:
		return float(m.group(2))
	else:
		return None

