# coding: utf-8

import sys
import re
import utility
from plugins import Plugin
from commands import Command
import command_catcher

class Spot(object):
	def __init__(self, type, hash, format):
		self.type = type
		self.hash = hash
		self.format = format

	def URI(self):
		return "spotify:%s:%s" % (type, hash)

	def URL(self):
		return "http://open.spotify.com/%s/%s" % (type, hash)

class SpotifyConvertPlugin(Command):
	hooks = ['on_privmsg']
	spots = {}
	spot_list = []

	def __init__(self):
		pass

	def spot_lookup(self, type, hash):
		tempSpot = Spot(type, hash, 'URI')
		res = self.spot_lookup_direct(tempSpot)
		if res:
			return res
		else:
			return "couldn't find shit, captain!"

	def get_properties(self, url):
		response = utility.read_url(url)
		data = response["data"]

		pattern = r"<meta property=\"og:(.*?)\" content=\"(.*?)\" />"
		return dict(re.findall(pattern, data))

	def spot_lookup_direct(self, theSpot):
		url = "http://open.spotify.com/%s/%s" % (theSpot.type, theSpot.hash)

		p = self.get_properties(url)

		artist = None
		track = None
		album = None

		if p["type"] == "song":
			artist = self.get_properties(p["artist"])["title"]
			track = p["title"]
			album = self.get_properties(p["album"])["title"]
		elif p["type"] == "album":
			artist = self.get_properties(p["artist"])["title"]
			album = p["title"]

		output = "%s: %s | %s" % (artist, track, album)

		if not track:
			output = "%s: %s" % (artist, album)

		if not album:
			output = "%s" % artist

		if not artist:
			return None

		return output


	def spot_lookup_direct_old(self, theSpot):
		url = "http://spotify.url.fi/%s/%s" % (theSpot.type, theSpot.hash)
		response = utility.read_url(url)
		data = response["data"]

		# Commence data mining

		artist = re.search(r"<span>Artist</span>\s*<a.*?>(?P<artist>.+?)</a>", data, re.DOTALL)
		if artist: artist = artist.group(1)

		album = re.search(r"<span>Album</span>\s*<a.+?>(?P<album>.+?)</a>", data, re.DOTALL)
		if album: album = album.group(1)

		year = re.search(r"<span>Year</span>\s*(?P<year>.+?)\s*</p>", data, re.DOTALL)
		if year: year = year.group(1)

		track = re.search(r"<span>Track</span>\s*<a.+?>(?P<track>.+?)</a>", data, re.DOTALL)
		if track: track = track.group(1)

		length = re.search("<span>Length</span>\s*(?P<length>.+?)\s*</p>", data, re.DOTALL)
		if length: length = length.group(1)

		output = "%s: %s | %s (%s)" % (artist, track, album, year)

		if not track:
			output = "%s: %s (%s)" % (artist, album, year)

		if not album:
			output = "%s" % artist

		if not artist:
			return None

		return output

	def on_privmsg(self, bot, source, target, message):
		m = re.search(r'http://open\.spotify\.com/(?P<type>.+?)/(?P<hash>\w+)', message)
		prot = 'URL'
		if not m:
			prot = 'URI'
			m = re.search(r'spotify:(?P<type>.+?):(?P<hash>\w+)', message)
		if m:
			type = m.group('type')
			hash = m.group('hash')
			spot = Spot(type, hash, prot)
			self.spots[target] = spot
			self.save_last_spot(target)
			res = self.spot_lookup_direct(spot)

			if res:
				bot.tell(target, res)

	def save_last_spot(self, target):
		self.spot_list.append(self.spots[target])
		self.save_spots()


	def trig_spotify(self, bot, source, target, trigger, argument):
		if argument:
			m = re.search(r'http://open\.spotify\.com/(?P<type>.+?)/(?P<hash>\w+)', argument)

			if (not m):
				m = re.search(r'spotify:(?P<type>.+?):(?P<hash>\w+)', argument)

			if m:
				return self.spot_lookup(m.group("type"), m.group("hash"))

			else:
				return "Couldn't make sense of that."

		elif target in self.spots.keys():
			m = self.spots[target]
			if m:
				return self.spot_lookup_direct(m)
			else:
				return 'I haven\'t seen any urls here yet.'


	def save_spots(self):
		utility.save_data("spots2", self.spot_list)


	def load_spots(self):
		self.spot_list = utility.load_data("spots2", [])


	def on_load(self):
		self.load_spots()


	def save(self):
		pass


	def on_modified_options(self):
		self.save()
