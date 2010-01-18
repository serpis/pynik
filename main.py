# coding: latin-1

from ircbot import IRCBot
from httpsrv import http_server
import time
import settings
import datetime
import sys

if settings.nick == "CHANGEME":
	print "---> Please customize settings.py and try again. <---"
	sys.exit(0);

bot = IRCBot(settings.server_address, settings.server_port, settings.nick, settings.username, settings.realname)

#web_server = http_server.HTTPServer(8000)

botnik_picture_data = None


def handle_request(request):
	if request.request_path == "/botnik.png":
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

	c = None
	if bot.is_connected():
		c = "connected"
	else:
	 	c = "disconnected"

	data = "I think that I am %s.<p><img src=\"botnik.png\"><p>" % c

	data += "Conversation:<p><pre>"
	for line in bot.client.lines:
		data += line.replace("<", "&lt;").replace(">", "&gt;") + "\n"
	data += "</pre>"

	web_server.respond_200(request, data)

#web_server.register_handle_request_callback(handle_request)
	
#bot.add_timer(datetime.timedelta(0, 60), True, bot.send, "PRIVMSG #botnik :this is to keep me alive :O")

while True:
	bot.tick()
	#web_server.tick()
	time.sleep(0.1)
