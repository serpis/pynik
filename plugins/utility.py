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

def read_url(url):
	import urllib2
	import socket
	
	# THIS AFFECTS SOCKETS GLOBALLY AND SHOULD _NOT_ BE USED!!!
	timeout_time = socket.getdefaulttimeout()
	socket.setdefaulttimeout(15)
	

	request = urllib2.Request(url)
	request.add_header('User-Agent', 'PynikOpenAnything/1.0 +')

	opener = urllib2.build_opener()

	web_resource = None
	data = ''
	try:
	
		web_resource = opener.open(request)
		data = web_resource.read()
	finally:
		if web_resource:
			web_resource.close()

		
		# THIS AFFECTS SOCKETS GLOBALLY AND SHOULD _NOT_ BE USED!!!
		socket.setdefaulttimeout(timeout_time)
	return data
