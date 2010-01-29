# coding: utf-8
import re
import utility
import string
import os
import urllib
import httplib
import pickle
import datetime
from commands import Command

# GET /input/i=22%3A00+%2B8h
# ->
#   asynchronousPod('pod.jsp?id=MSP452196e7f3bha23260d0000203695bbfdee778g&s=7', '0300', '22%3A00+%2B8h', '' ); 
#   recalculate('recalculate.jsp?id=MSP453196e7f3bha23260d000022932508hh587agi&asynchronous=pod&i=22%3A00+%2B8h&s=7');

# GET /input/recalculate.jsp?id=MSP453196e7f3bha23260d000022932508hh587agi&asynchronous=pod&i=22%3A00+%2B8h&s=7
# ->
#   asynchronousPod('pod.jsp?id=MSP567196e7f3bh9ehi1e70000598h44c1c76657dh&s=7', '0233', '22%3A00+%2B8h');
#   asynchronousPod('pod.jsp?id=MSP568196e7f3bh9ehi1e700004027bi5agac51ie7&s=7', '0266', '22%3A00+%2B8h');
#   asynchronousPod('pod.jsp?id=MSP569196e7f3bh9ehi1e700004d9bf82d55cdfec4&s=7', '0400', '22%3A00+%2B8h');


class WolframAlpha(Command):
	def __init__(self):
		self.lastrun = None
	
	def utf82iso(self, s):
		try:
			return s.decode("utf-8").encode("iso-8859-1")
		except:
			return s

	def trig_alpha(self, bot, source, target, trigger, argument, network, **kwargs):
		# If to early
		if self.lastrun and datetime.datetime.now() - self.lastrun < datetime.timedelta(seconds=3):
			return "Alpha is not ready yet, wait a while."

		baseurl = "http://www83.wolframalpha.com/input/"
		url = baseurl + "?i=" + utility.escape(argument)

		bot.tell(network, target, "Seeking audiance with Alpha, this might take a while...")
		print "Trying to connect"


		# Ugly hack FIXME
		import signal
		signal.alarm(20)		
	 
		response = utility.read_url(url)
		data = response["data"]

		#print data
		datas = [data]
		answers = {}
		answer = None
		while datas:
			data = datas.pop(0)
			data = data.replace("\r", "")
			
			for line in data.split("\n"):
				# Descriptive text
				search = re.search("<span>([^<]*)</span>", line)
				if search:
					print search.group(1)
					if answer:
						#print answer
						if not answers.has_key(answer['desc']):
							answers[answer['desc']] = answer
						
					answer = {'desc': search.group(1), 'answer': []}

				# Data!
				search = re.search('alt="([^"]*)"', line)
				if search:
					print search.group(1)
					if answer:
						answer['answer'].append(search.group(1))
					else:
						print "alpha: SHOULD NOT HAPPEN, " + search.group(1) 


				# Download pod!
				search = re.search("asynchronousPod\('([^']*)'[^']*'([^']*)'[^']*'([^']*)'", line)
				if search:
					posturl = search.group(1) + "&i=" +  search.group(3)
					print "Posting for pod at %s ..." % posturl
					
					params = urllib.urlencode({"asynchronous": 'true'})
					headers = {"Host": "www83.wolframalpha.com",
						   "Connection": "close",
						   #"Via": "1.1 tinyproxy (tinyproxy/1.6.4)",
						   "Accept": "text/html, */*",
						   "Referer": "http://www83.wolframalpha.com/input/?i=22%3A00+%2B8h",
						   "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; sv-SE; rv:1.9.0.11) Gecko/2009060215 Firefox/3.0.11 (.NET CLR 3.5.30729)",
						   "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
						   #"Cookie": "WR_SID=85.229.221.66.1248096225817695; JSESSIONID=D6E0FA92ED59A69CC41C43244589B153",
						   #"Accept-Encoding": "gzip,deflate",
						   "Accept-Language": "en-us,en;q=0.7,sv;q=0.3",
						   "X-Requested-With": "XMLHttpRequest",
						   }

					conn = httplib.HTTPConnection("www83.wolframalpha.com:80")
					conn.request("POST", "/input/" + posturl, params, headers)

					response = conn.getresponse()
					
					#print response.status, response.reason
					d = response.read()
					#print "'" + d + "'"
					datas.append(d)
					
					conn.close()


				# Recalculate for moar pods
				search = re.search("recalculate\('([^']*)'\)", line)
				if search and search.group(1).strip():
					print "GETs recalculate '%s' ..." % search.group(1)

					params = urllib.urlencode({})

					headers = {"Host": "www83.wolframalpha.com",
						   "Connection": "close",
						   #"Via": "1.1 tinyproxy (tinyproxy/1.6.4)",
						   "Accept": "text/html, */*",
						   "Referer": "http://www83.wolframalpha.com/input/?i=22%3A00+%2B8h",
						   "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; sv-SE; rv:1.9.0.11) Gecko/2009060215 Firefox/3.0.11 (.NET CLR 3.5.30729)",
						   "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
						   #"Cookie": "WR_SID=85.229.221.66.1248096225817695; JSESSIONID=D6E0FA92ED59A69CC41C43244589B153",
						   #"Accept-Encoding": "gzip,deflate",
						   "Accept-Language": "en-us,en;q=0.7,sv;q=0.3",
						   "X-Requested-With": "XMLHttpRequest",
						   }

					conn = httplib.HTTPConnection("www83.wolframalpha.com:80")
					conn.request("GET", "/input/" + search.group(1), params, headers)

					response = conn.getresponse()
					
					#print response.status, response.reason
					datas.append(response.read())
					
					conn.close()
					
		print "Answers:" + str(answers)

		restult = ""
		input_key = ""
		if answers.has_key("Input interpretation:"):
			input_key = "Input interpretation:"
		elif answers.has_key("Input:"):
			input_key = "Input:"
		else:
			return "Alpha does not understand."

		# Create result
		result = "Alpha on '%s' says " % answers[input_key]["answer"][0]

		if answers.has_key("Result:"):
			for ans in answers["Result:"]["answer"]:
				result += " " + ans
				result += "; "

		for desc,answer in answers.iteritems():
			if desc not in ("Please make a selection:", "Input interpretation:", "Result:"):
				result += desc
				for ans in answer["answer"]:
					result += " " + ans
				result += "; "
		result = result.replace("\\n", " ")
		result = result.replace("|", "")
		result = re.sub("( ){2,}", " ", result)

		result = re.sub(" hour[s]*", "h", result)
		result = re.sub(" minute[s]*", "m", result)
		result = re.sub(" seconds[s]*", "s", result)

		result = result[:-1] + ";"

		self.lastrun = datetime.datetime.now()

		print result
		return result
