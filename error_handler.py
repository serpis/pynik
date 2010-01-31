# -*- coding: utf-8 -*-

import sys
import time

def output_message(message, severity=3):
	# Maybe it would be nice to output in different formats depending on
	# how severe the error is. Not implemented yet though.
	
	string = time.strftime("[%H:%M:%S] ")
	
	try:
		string += str(message)
	except:
		string += "Unknown error occured, non-printable message sent. Shouldn't happen :S"
	
	# For now, just send everything to stderr.
	print >> sys.stderr, string

