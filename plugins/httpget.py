import sys
import re
import urllib
from socket import *

def write(s, text):
	s.send(text)
	s.send("\r\n")

class http_get_request:
	def __init__(self, file):
		self.file = file
		self.headers = []

	def add_header(self, name, value):
		self.headers.append((name, value))

	def send(self, s):
		write(s, "GET %s HTTP/1.0" % self.file)
		write(s, "\r\n".join(map(lambda x: "%s: %s" % x, self.headers)))
		write(s, "")
		write(s, "")

def read_line(s):
	line = ""

	while True:
		line += s.recv(1)

		if line and line[-1:] == "\n":
			line = line[0:-1]
			if len(line) and line[-1] == "\r":
				line = line[0:-1]

			return line

def read_http_headers(s):
	m = re.match("^(.+?) (.+?) (.+)$", read_line(s))
	protocol, response_num, response_string = m.groups()
	headers = {}

	while True:
		line = read_line(s)
		if len(line) == 0:
			break

		m = re.match("^(.+?) (.+)$", line)
		if m:
			headers[m.group(1)[0:-1]] = m.group(2)

	return (protocol, int(response_num), response_string, headers)

def read_http_data(s, length):
	data = ''
	while not length or len(data) < length:
		to_receive = 1024
		if length:
			to_receive = min(length - len(data), 1024)

		new_data = s.recv(to_receive)

		if new_data:
			data += new_data
		else:
			break

	return data

class AppURLopener(urllib.FancyURLopener):
	version = "Pynik/0.1"

def read_url(url):
	m = re.match("^(.{3,5}):\/\/([^\/]*)(:?\d*)(\/.*?)?$", url)
	if m:
		protocol, address, port, file = m.group(1, 2, 3, 4)

		if protocol == 'https':
			# Use the built-in functions

			try:
				urllib._urlopener = AppURLopener()
				file = urllib.urlopen(url)
			except IOError:
				return None

			result = { "url": file.geturl(),
						"data": file.read(1024*1024),
						"info": file.info() }

			file.close()
			return result

		elif protocol != 'http':
			print "Only http(s) is supported at this moment."
			return None
		else:
			if not port:
				port = 80
			if not file:
				file = '/'

			#print "Connecting to %s" % address

			request = http_get_request(file)
			request.add_header("User-Agent", "Pynik/0.1")
			request.add_header("Accept", "*/*")
			request.add_header("Host", address)

			s = socket(AF_INET, SOCK_STREAM)

			s.connect((address, port))
			request.send(s)

			protocol, response_num, response_string, headers = read_http_headers(s)

			if response_num == 301 or response_num == 302:
				s.close()

				# Let's do some simple loop detection...
				if url == headers['Location']:
					print "Redirect loop discovered at: %s" % headers['Location']
					return None
				else:
					print "Site moved to: %s" % headers['Location']
					return read_url(headers['Location'])
			elif response_num == 200:
				#print "Got response 200. Sweet!"
				length = 1024*1024 # max one megabyte
				if "Content-Length" in headers:
					length = min(length, int(headers["Content-Length"]))

				data = read_http_data(s, length)

				s.close()

				return { "url": url, "data": data }
			else:
				print "Got unhandled response code: %s" % response_num
				return None
	else:
		print "NOT AN URL: %s" % url
		return None
