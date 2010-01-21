from autoreloader.autoreloader import AutoReloader # Do not remove
class Settings(AutoReloader):                      # these two lines

	# Sample config, all options are mandatory
	# Bot currently only supports one network.
	networks = {
		"quakenet": {"server_address": "irc.example.com",
			     "server_port": 6667,
			     "nick": "CHANGEME",
			     "username": "CHANGEME",
			     "realname": "CHANGEME",
			     },
		}

	admin_channel = "#example"
	admin_adminnicks = ["CHANGEME"]
