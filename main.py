# coding: latin-1

from ircbot import IRCBot
from httpsrv import http_server
import time

bot = IRCBot()
bot.connect("port80.se.quakenet.org", 6667)
bot.send("USER botnik * * :botnik")
bot.send("NICK botnik2")

web_server = http_server.HTTPServer(8000)

botnik_picture_data = None

def handle_request(request):
	print request.request_path
	if "tickle" in request.request_path:
		bot.tell("#c++.se", "stop that!")
	elif request.request_path == "/botnik.png":
		global botnik_picture_data

		if not botnik_picture_data:
			try:
				file = open("botnik.png")
				botnik_picture_data = file.read()
				file.close()
			except:
				web_server.respond_200(request, "Couldn't send image...")
		web_server.respond_200(request, botnik_picture_data, "image/png")
		return

	web_server.respond_200(request, "If you can see this, I'm online.<p><img src=\"botnik.png\">")

web_server.register_handle_request_callback(handle_request)

while True:
	bot.tick()
	web_server.tick()
	time.sleep(0.1)
