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
	return urllib.quote_plus(str)
	
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
	import urllib

	data = ''
	datasource = None
	
	try:
		datasource = urllib.urlopen(url)
		data = datasource.read()
	finally:
		if datasource:
			datasource.close()
	return data
