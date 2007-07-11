import sys
from plugins import Plugin
import htmlentitydefs

class UtilityPlugin(Plugin): 
	def unescape(self, url):
		def fromhtml(s):
			try: return htmlentitydefs.entitydefs[s.group(1)]
			except KeyError: return chr(int(s.group(1)))
		return re.sub("&#?(\w+);", fromhtml, text)
		
	def get_all_subclasses(self, c):
		l = [c]
		for subclass in c.__subclasses__():
			l.extend(self.get_all_subclasses(subclass))
		return l
