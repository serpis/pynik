# -*- coding: utf-8 -*-

import utility
from commands import Command

import re
from json import JSONDecoder

class SpotifyRef(object):
	def __init__(self, target_type, spotify_hash):
		self.type = target_type
		self.hash = spotify_hash

	def URI(self):
		return u"spotify:%s:%s" % (self.type, self.hash)

	def URL(self):
		return u"http://open.spotify.com/%s/%s" % (self.type, self.hash)


class SpotifyCommand(Command):
	hooks = ['on_privmsg']
	references = {}
	api_base_url = u"http://78.31.8.28/" # http://ws.spotiy.com/ is official but seems unstable

	def __init__(self):
		pass

	def lookup(self, target_type, spotify_hash):
		temp_ref = SpotifyRef(target_type, spotify_hash)
		res = self.lookup_direct(temp_ref)
		if res:
			return res
		else:
			return u"No metadata found :("

	def lookup_direct(self, reference):
		decoder = JSONDecoder()
		api_url = self.api_base_url + u"lookup/1/.json?uri=" + reference.URI()
		response = utility.read_url(api_url)

		if not response:
			return None

		try:
			data = decoder.decode(response['data'])
		except StandardError:
			return None

		if not data.get(u"info"):
			return None

		# Album reference
		if reference.type == u"album":
			metadata = data.get(u"album", {})
			album = metadata.get(u"name", u"Unknown album")
			artist = metadata.get(u"artist", u"Unknown artist")
			year = metadata.get(u"released", u"Unknown year")
			return u"%s: %s (%s)" % (artist, album, year)

		# Artist reference
		elif reference.type == u"artist":
			metadata = data.get(u"artist", {})
			artist = metadata.get(u"name", u"Unknown artist")
			return u"%s" % artist

		# Track reference
		elif reference.type == u"track":
			#return u"track"
			# Extract some dicts from the data
			metadata = data.get(u"track", {})
			metadata_album = metadata.get(u"album", {})
			metadata_artists = metadata.get(u"artists", [{}])

			# Extract info from the dicts
			album = metadata_album.get(u"name", u"Unknown album")
			artists = map(lambda artist: artist.get(u"name", u"Unknown artist"), metadata_artists)
			artist = ", ".join(artists)
			duration = metadata.get(u"length", u"0.0")
			popularity = metadata.get(u"popularity", u"0.0")
			track = metadata.get(u"name", u"Unknown track")
			year = metadata_album.get(u"released", u"Unknown year")

			# Convert strings to floats
			try:
				duration = float(duration)
			except ValueError:
				duration = 0.0;
			try:
				popularity = float(popularity)
			except ValueError:
				popularity = 0.0;

			# Construct result
			return u"%s: %s | %s (%s) | Track popularity %d%%, Track duration %d:%02d" % \
					(artist, track, album, year, int(round(popularity*100)), duration / 60, duration % 60)

		# Unsupported reference
		else:
			return None

	def on_privmsg(self, bot, source, target, message):
		m = re.search(r'http://open\.spotify\.com/(?P<type>.+?)/(?P<hash>\w+)', message)
		prot = 'URL'
		if not m:
			prot = 'URI'
			m = re.search(r'spotify:(?P<type>.+?):(?P<hash>\w+)', message)
		if m:
			reference = SpotifyRef(m.group('type'), m.group('hash'))
			self.references[target] = reference
			self.save_refs()
			# Non-escaped . is intended, because mainstream pynik lacks a way to get trigger char
			if not re.match(r'.spotify .+', message):
				res = self.lookup_direct(reference)
				if res:
					bot.tell(target, res.encode("utf-8"))

	def trig_spotify(self, bot, source, target, trigger, argument):
		"""Retrieves metadata about Spotify albums, artists and tracks. | This product uses a SPOTIFY API but is not endorsed, certified or otherwise approved in any way by Spotify. Spotify is the registered trade mark of the Spotify Group."""

		# Look up the argument
		if argument:
			m = re.search(r'http://open\.spotify\.com/(?P<type>.+?)/(?P<hash>\w+)', argument)
			if not m:
				m = re.search(r'spotify:(?P<type>.+?):(?P<hash>\w+)', argument)
			if m:
				return self.lookup(m.group("type"), m.group("hash")).encode("utf-8")
			else:
				return "Couldn't make sense of that."

		# Look up the last posted link
		res = None

		if target in self.references.keys():
			ref = self.references[target]
			if ref:
				res = u" | ".join([self.lookup_direct(ref), ref.URL()])
		
		if res:
			return res.encode("utf-8")
		else:
			return 'I haven\'t seen any Spotify links here yet.'

	def save_refs(self):
		utility.save_data("spotify", self.references)

	def load_refs(self):
		self.references = utility.load_data("spotify", {})

	def on_load(self):
		self.load_refs()

