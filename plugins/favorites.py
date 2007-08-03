# coding: latin-1

from __future__ import with_statement
import pickle
from commands import Command
import re
import utility

class FavoriteCommands(Command):
	triggers = ['setfav', 'fav', 'favorites', 'delfav']
	favorites = {}

	def __init__(self):
		pass

	def get_options(self):
		return ['favorites']

	def on_delfav(self, bot, source, target, trigger, argument):
		if source == 'serp':
			m = re.search('^(\w+)', argument)
		
			if m:
				fav_trig = m.group(1)

				if fav_trig in self.favorites:
					del self.favorites[fav_trig]
	
					self.save()

					bot.tell(target, 'Favorite \'' + fav_trig  + '\' deleted.')

	def on_setfav(self, bot, source, target, trigger, argument):
		m = re.search('^(\w+)\s+((ftp:\/\/|http:\/\/|https:\/\/)[^\s]+)$', argument)
		
		if m:
			fav_trig = m.group(1)
			fav_url = m.group(2)
			
			self.favorites[fav_trig] = fav_url
	
			self.save()

			bot.tell(target, 'Favorite \'' + fav_trig  + '\' added.')

	def on_favorites(self, bot, source, target, trigger, argument):
		from copy import copy
		bot.tell(target, 'Favorites: ' + ', '.join(sorted(self.favorites.keys())) + '.')
	
	def on_fav(self, bot, source, target, trigger, argument):
		m = re.search('(\S+) ?(.*)$', argument)
		
		if m:
			fav_trig = m.group(1);
			fav_args = m.group(2);

			if fav_trig in self.favorites:
				url = self.favorites[fav_trig]
				url = url.replace('%s', utility.escape(fav_args).replace('%2F', '/'))
				bot.tell(target, url)
			else:
				bot.tell(target, 'No such favorite \'' + fav_trig + '\'.')
	
	def on_trigger(self, bot, source, target, trigger, argument):
		{
			'setfav': self.on_setfav,
			'fav': self.on_fav,
			'favorites': self.on_favorites,
			'delfav': self.on_delfav
		}[trigger](bot, source, target, trigger, argument)

	def save(self):
		with open('data/favorites.txt', 'w') as file:
			p = pickle.Pickler(file)

			p.dump(self.favorites)

	def on_modified_options(self):
		self.save()

	def on_load(self):
		self.favorites = {}

		with open('data/favorites.txt') as file:
			if file:
				unpickler = pickle.Unpickler(file)

				self.favorites = unpickler.load()

	def on_unload(self):
		self.favorites.clear()

