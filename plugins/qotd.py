# coding: latin-1

from __future__ import with_statement
from commands import Command

class FavoriteCommands(Command):
	triggers = ['setfav', 'fav', 'favorites', 'delfav']
	favorites = {}

	def __init__(self):
		pass

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
		l = copy(self.favorites.keys())
		l.sort()
		bot.tell(target, 'Favorites: ' + ', '.join(l) + '.')
	
	def on_fav(self, bot, source, target, trigger, argument):
		m = re.search('(\S+)\s+(.*)$', argument)
		
		if m:
			fav_trig = m.group(1);
			fav_args = m.group(2);

			if fav_trig in self.favorites:
				url = self.favorites[fav_trig]
				url = url.replace('%s', fav_args)
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
		file = open('data/favorites.txt', 'w')

		for key in self.favorites.keys():
			line = key + ' ' + self.favorites[key]

			file.write(line)
			file.write('\n')

		file.close()

	def on_load(self):
		self.favorites.clear()

		file = open('data/favorites.txt', 'r')
		
		while True:
			line = file.readline()
			if not line:
				break

		#with open('data/favorites.txt', 'r') as file:
		#	for line in file:
			m = re.search('^(.+?)\s(.+)$', line)

			if m:
				key = m.group(1)
				url = m.group(2)

				self.favorites[key] = url

		file.close()
	
	def on_unload(self):
		self.favorites.clear()

