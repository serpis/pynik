# coding: latin-1
import time
import datetime
import os
import sys
import pdb
import gc

try:
	import settings
except ImportError:
	print "---> Please copy settings.sample.py to settings.py and customize it. <---"
	sys.exit(0)

import ircbot
from httpsrv import http_server

bot = ircbot.IRCBot(settings.Settings())

#web_server = http_server.HTTPServer(host="127.0.0.1", port=8000)
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
#	if bot.is_connected(): #FIXME
#		c = "connected"
#	else:
#	 	c = "disconnected"

	data = "I think that I am %s.<p><img src=\"botnik.png\"><p>" % c

	data += "Conversation:<p><pre>"
	for line in bot.client.lines:
		data += line.replace("<", "&lt;").replace(">", "&gt;") + "\n"
	data += "</pre>"

	web_server.respond_200(request, data)

#web_server.register_handle_request_callback(handle_request)
	
bot.add_timer(datetime.timedelta(0, 600), True, bot.send_all_networks, "PING :iamabanana")
sys.path += [os.path.join(sys.path[0], "httpsrv"), os.path.join(sys.path[0], "ircclient"),
	     os.path.join(sys.path[0], "plugins")]

def Tick():
	while True:
		try:
			if bot.need_reload.has_key('main') and bot.need_reload['main']:
				reload(ircbot)
				reload(settings)
				print "Collected %s objects out of %s. Garbarge are %s objects." % (gc.collect(2), 
					len(gc.get_objects()), len(gc.garbage))
				bot.need_reload['main'] = False
				bot.on_reload()

			bot.tick()
			#web_server.tick()

			time.sleep(0.1)
		except KeyboardInterrupt:
			print ""
			print "Entering debug mode, use c(ontinue) to exit. Don't stay here to long."
			pdb.set_trace()
		except:
			raise

# Run bot with debugger
pdb.run(Tick())
