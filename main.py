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

bot = ircbot.IRCBot(settings.Settings())
bot.add_timer(datetime.timedelta(0, 600), True, bot.send_all_networks, "PING :iamabanana")

# Add paths for debugger
sys.path += [os.path.join(sys.path[0], "ircclient"), os.path.join(sys.path[0], "plugins")]

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

			time.sleep(0.1)
		except KeyboardInterrupt:
			print ""
			print "Entering debug mode, use c(ontinue) to exit. Don't stay here to long."
			print "This is " + bot.settings.networks.values()[0]["nick"]
			pdb.set_trace()
		except:
			raise

# Run bot with debugger
pdb.run(Tick())
