# -*- coding: utf-8 -*-

import sys

def output_message(message, severity=5):
	# Maybe it would be nice to output in different formats depending on
	# how severe the error is. Not implemented yet though.
	
	try:
		# For now, just send everything to stderr.
		print >> sys.stderr, message
	except:
		print >> sys.stderr, "Unknown error occured, non-printable message sent. Shouldn't happen :S"

