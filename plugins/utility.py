# coding: utf-8

import sys
from plugins import Plugin
import htmlentitydefs
import re
import signal

class TimeoutException(Exception):
	pass

def unescape(str):
	def fromhtml(s):
		try: return htmlentitydefs.entitydefs[s.group(1)]
		except KeyError: return chr(int(s.group(1)))
	return re.sub("&#?(\w+);", fromhtml, str)

def escape(str):
	import urllib
	t = {
		'%E5': 'å',
		'%E4': 'ä',
		'%F6': 'ö',
		'%C5': 'Å',
		'%C4': 'Ä',
		'%D6': 'Ö'
	}

	s = urllib.quote_plus(str)

	for key in t.keys():
		s = s.replace(key, t[key])

	return s
	
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
