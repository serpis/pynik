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
	api_base_url = u"https://api.spotify.com/"

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
		if reference.type == u"album":
			endpoint = u"v1/albums/{id}"
		elif reference.type == u"artist":
			endpoint = u"v1/artists/{id}"
		elif reference.type == u"playlist":
			endpoint = u"v1/users/{user_id}/playlists/{playlist_id}"
			return None  # Unsupported by this plugin
		elif reference.type == u"track":
			endpoint = u"v1/tracks/{id}"
		else:
			return None  # Unsupported by this plugin

		api_url = self.api_base_url + endpoint.format(id=reference.hash)
		response = utility.read_url(api_url)

		if not response:
			return None

		try:
			data = JSONDecoder().decode(response['data'])
		except ValueError:
			return None

		if data.get(u"status"):
			return None
		else:
			return self._format_result(reference.type, data)

	def _format_result(self, type, data):
		if type == u"album":
			album = data.get(u"name", u"Unknown album")
			date = data.get(u"release_date", u"Unknown year")
			popularity = data.get(u"popularity", 0)

			artist_data = data.get(u"artists")
			if artist_data:
				artists = ", ".join(a.get(u"name", "???") for a in artist_data)
			else:
				artists = u"Unknown artist"

			return u"%s: %s (%s) | Album popularity %s%%" % \
				(artists, album, date, popularity)

		elif type == u"artist":
			artist = data.get(u"name", u"Unknown artist")
			popularity = data.get(u"popularity", 0)

			return u"%s | Artist popularity %s%%" % (artist, popularity)

		elif type == u"track":
			track = data.get(u"name", u"Unknown track")
			track_number = data.get(u"track_number", "???")
			popularity = data.get(u"popularity", 0)
			duration = data.get(u"duration_ms", 0) / 1000.0

			album_data = data.get(u"album", {})
			album = album_data.get(u"name", u"Unknown album")

			artist_data = data.get(u"artists")
			if artist_data:
				artists = ", ".join(a.get(u"name", "???") for a in artist_data)
			else:
				artists = u"Unknown artist"

			return u"%s: %s | Track #%s on %s | Track popularity %d%%, Track duration %d:%02d" % \
				(artists, track, track_number, album, popularity,
				 int(duration / 60), round(duration % 60))

	def on_privmsg(self, bot, source, target, message):
		m = re.search(r'https?://open\.spotify\.com/(?P<type>.+?)/(?P<hash>\w+)', message)
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
			m = re.search(r'https?://open\.spotify\.com/(?P<type>.+?)/(?P<hash>\w+)', argument)
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

