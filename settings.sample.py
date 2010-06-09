from autoreloader.autoreloader import AutoReloader # Do not remove
class Settings(AutoReloader):                      # these two lines

	# Sample config, all options are mandatory
	networks = {
		"example": {"server_address": "irc.example.com",
			     "server_password": "mypassword", # optional, omit if unused.
			     "server_port": 6667,
			     "nick": "CHANGEME",
			     "username": "CHANGEME",
			     "realname": "CHANGEME",
			     "channels": [["#CHANGEME"], ["#channel", "password"], ],
			     },
		}

	admin_network = "example"
	admin_channel = "#example"
	admin_adminnicks = ["CHANGEME"]

	trigger = "."
	
	# Plugins that will be loaded on startup from plugins/
	# Use this directory to view all available Plugins and to add your own.
	plugins = ['plugins', 'command_catcher', 'commands', 'standard',
		   'reloader', 'options', 'utility']

	# If you want to enable more plugins comment out the above
	# and uncomment the ones below.
	#plugins = ['plugins', 'command_catcher', 'commands', 'standard',
	#	   'reloader', 'options', 'utility',
	#	   "aduno", "alpha", "char", "code", "compliment", "countdown", 
	#	   "down", "example_plugin", "favorites", "festern_bbq", "fml", 
	#	   "food", "game_plugin", "give", "googlefight", "ical_parser", 
	#	   "icq", "imdb", "isitfriday", "kolli", "lithcourse", "magic8ball", 
	#	   "mat", "metacritic", "nelson", "nextep", "notes", "pi", 
	#	   "postnr", "prisjakt", "pylisp", "qotd", "randombuy", 
	#	   "reminder", "roulette", "rss", "scale", "spotify", "stava", 
	#	   "systembolaget", "tenta", "timezone", "title_reader", "tv", 
	#	   "tyda", "yrno"]

