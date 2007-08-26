# coding: utf-8

import os
import re
import datetime
from commands import Command

class SvnCommand(Command):
	subscribers = {}

	def get_options(self):
		return ['subscribers']

	def trig_svn(self, bot, source, target, trigger, argument):
		url = argument
		if not len(url):
			url = 'http://stalverk80.se/svn/pynik'
		p = os.popen2(['svn', 'info', url])
		stdin, stdout =  p

		data = stdout.read()

		error = True

		m = re.search("Last Changed Author:\s+(.+)\nLast Changed Rev:\s+(.+)\nLast Changed Date:\s+(.+)", data)

		if m:
			last_author, last_rev, last_date = m.group(1, 2, 3)
			
			m = re.search('^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})', last_date)
			
			if m:
				error = False

				args = map(int, m.groups())
				
				d = datetime.datetime(*args)

				return "Last revision was %s by %s at %s." % (last_rev, last_author, d)


		if error:
			return "Could not retrieve that information for some reason."
