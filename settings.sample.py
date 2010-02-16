from autoreloader.autoreloader import AutoReloader # Do not remove
class Settings(AutoReloader):                      # these two lines

	# Sample config, all options are mandatory
	networks = {
		"example": {"server_address": "irc.example.com",
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

