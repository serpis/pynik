# -*- coding: utf-8 -*-

import subprocess
import re
import datetime
from commands import Command

class SvnCommand(Command):
	subscribers = {}

	def get_options(self):
		return ['subscribers']

	def trig_svn(self, bot, source, target, trigger, argument):
		result = ""
		url = argument.strip()
		
		if not len(url):
			url = 'http://stalverk80.se/svn/pynik'
			result = "No argument given, result for my own repository: ";
		
		# Execute 'svn info' in anonymous, non-interactive mode
		command = [
			'svn',
			'info',
			'--no-auth-cache',
			'--username',
			'anonymous',
			'--non-interactive',
			url]
		p = subprocess.Popen(
				command,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				close_fds=True,
				env={"LANGUAGE": "en_US:en"})
	
		m = re.search(
				"Last Changed Author:\s+(.+)\nLast Changed Rev:\s+(.+)\nLast Changed Date:\s+(.+)",
				 p.stdout.read())
		
		if m:
			# Seems like we have parseable data
			last_author, last_rev, last_date = m.group(1, 2, 3)
			m = re.search('^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})', last_date)
			
			if m:
				# Result found, prepare and return
				args = map(int, m.groups())
				d = datetime.datetime(*args)
				result += url + " - Last revision was %s by %s at %s." % (last_rev, last_author, d)
				return result
	
		# Hrm, no result found, let's try to find out why
		error = p.stderr.read()
		if re.search('Connection refused', error) or \
				re.search('could not connect to server', error) or \
				re.search('Host not found', error):
			result += "Could not connect to the specified URL :("
		elif re.search('authorization failed', error) or \
				re.search("403 Forbidden", error):
			result += "Hrm, that repository is non-public :/"
		else:
			m = re.search('svn: Server sent unexpected return value \((.+?)\) in response to ',
					error)
			if m:
				result += "Oops, the server replied \"" + m.group(1) + "\" :O"
			else:
				result += "Could not retrieve that information for some reason :S"
		
		return result
