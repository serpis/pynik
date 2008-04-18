import socket
import re
import datetime

class ClientRequest:
	def __init__(self, address, data, socket):
		self.source_address = address
		self.socket = socket

		self.headers = {}

		self.cookies = {}

		lines = data.split("\r\n")

		request_line = lines[0]
		lines = lines[1:]

		m = re.search("^(\w+) (.+) (HTTP\/...)$", request_line)
		if m:
			method, request_uri, version = m.group(1, 2, 3)

			self.method = method
			self.request_path = request_uri
			self.version = version

			for line in lines:
				if line:
					m = re.search("^(\S+): (.+)$", line)
					if m:
						name, value = m.group(1, 2)
						self.headers[name] = value

		if "Cookie" in self.headers:
			cookies = self.headers["Cookie"]

			for trash1, key, value, trash2 in re.findall("(^|:)(.*?)=(.*)(;|$)", cookies):
				self.cookies[key] = value

	def get_version(self):
		return self.version

	def get_method(self):
		return self.method

	def get_request_uri(self):
		return self.request_uri

	def get_header(self, name):
		if name in self.headers:
			return self.headers[name]
		else:
			return None

	def get_cookie(self, name):
		if name in self.cookies:
			return self.cookies[name]
		else:
			return None

	def __str__(self):
		return "%s %s %s %s" % (self.method, self.request_path, self.version, self.headers)

class ServerResponse:
	def __init__(self, status_code):
		self.version = "HTTP/1.1"
		self.status_code = status_code
		self.headers = {}
		self.content = None

	def add_header(self, key, value):
		self.headers[key] = value

	def remove_header(self, key):
		if key in self.headers:
			del self.headers[key]

	def set_content(self, content):
		self.content = content

		if content:
			self.add_header("Content-Length", str(len(content)))
		else:
			self.remove_header("Content-Length")

	def add_cookie(self, name, value, life_time=datetime.timedelta(1)):
		self.cookies[name] = (value, datetime.datetime.now()+life_time)

	def compile(self):
		lines = []

		status_line = "%s %d %s" % (self.version, self.status_code, "OK")
		lines.append(status_line)
		for key, value in self.headers.items():
			lines.append("%s: %s" % (key, value))

		data = "\r\n".join(lines) + "\r\n\r\n"

		if self.content:
			data += self.content

		return data

class HTTPServer:
	def __init__(self, port):
		self.handle_request_callback = None

		self.socket = socket.socket()
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind(("", port))
		self.socket.listen(10)

		self.socket.setblocking(False)

	def register_handle_request_callback(self, callback):
		self.handle_request_callback = callback

	def wait_for_request(self):
		s, address = self.socket.accept()
		#print "GOT CONNECTION!", s, address

		data = s.recv(65536)

		#s.close()

		return ClientRequest(address, data, s)

	def respond_404(self, request):
		response = ServerResponse(404)

		response.add_header("Content-Type", "text/html")
		response.add_header("Connection", "close")

		response.set_content("404 etc")

		self.respond(request, response)

	def respond_200(self, request, data, type = "text/html"):
		response = ServerResponse(200)

		response.add_header("Content-Type", type)
		response.add_header("Connection", "close")
		response.set_content(data)

		self.respond(request, response)

	def respond(self, request, response):
		data = response.compile()

		while data:
			sent = request.socket.send(data)
			if sent <= 0:
				return
			else:
				data = data[sent:]

		request.socket.close()

	def tick(self):
		try:
			request = self.wait_for_request()
			self.handle_request_callback(request)

		except socket.error:
			pass
