# coding: utf-8

from __future__ import with_statement
import pickle
from commands import Command
import re
import utility

class FavoriteCommands(Command):
	def __init__(self):
		self.favorites = {}

	def get_options(self):
		return ['favorites']

	def trig_delfav(self, bot, source, target, trigger, argument):
		if utility.has_admin_privileges(source, target):
			m = re.search('^([^\s]+)', argument)
		
			if m:
				fav_trig = m.group(1)

				if fav_trig in self.favorites:
					del self.favorites[fav_trig]
	
					self.save()

					return "Favorite %s deleted." % fav_trig

	def trig_setfav(self, bot, source, target, trigger, argument):
		m = re.search('^([^\s]+)\s+((ftp:\/\/|http:\/\/|https:\/\/)[^\s]+)$', argument)
		
		if m:
			fav_trig, fav_url = m.group(1, 2)
			
			self.favorites[fav_trig] = fav_url
	
			self.save()

			return "Favorite %s added." % fav_trig
		else:
			return "Syntax: setfav <trigger> <url>"

	def trig_favorites(self, bot, source, target, trigger, argument):
		from copy import copy
		bot.tell(target, 'Favorites: ' + ', '.join(sorted(self.favorites.keys())) + '.')

	def get_fav(self, trig, args):
		if trig in self.favorites:
			url = self.favorites[trig]
			url = url.replace('%s', utility.escape(args).replace('%2F', '/'))
			return url
		else:
			return None

	def trig_fav(self, bot, source, target, trigger, argument):
		m = re.search('(\S+) ?(.*)$', argument)
		
		if m:
			fav_trig = m.group(1);
			fav_args = m.group(2);

			fav = self.get_fav(fav_trig, fav_args)

			if fav:
				return fav
			else:
				return "No such favorite '%s'." % fav_trig
	
	def save(self):
		with open('data/favorites.txt', 'w') as file:
			p = pickle.Pickler(file)

			p.dump(self.favorites)

	def on_modified_options(self):
		self.save()

	def on_load(self):
		self.favorites = {}

		try:
			with open('data/favorites.txt') as file:
				unpickler = pickle.Unpickler(file)

				self.favorites = unpickler.load()
		except:
			pass

	def on_unload(self):
		self.favorites.clear()

