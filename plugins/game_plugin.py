# coding: utf-8

from __future__ import with_statement
from commands import Command
import random
import datetime
import pickle
import utility
import standard
import re

class Game:
	def __init__(self, name):
		self.name = name
		self.players = {}
		self.timeout = None
		self.time = None
		self.current_question = None
		self.timeout_streak = 0
		self.running = False 
		self.words = ["fur", "nigeria", "chewing gum", "cigar", "gamecube", "flower", "mp3", "bottle", "film", "radio", "knob", "fuck", "temperature", "milk", "mouse", "man", "wax", "pillow", "bicycle", "pub", "telephone", "stalk", "dog", "cat", "blacksmith", "glass", "door", "house", "metal", "lighter", "window", "mechanic", "camera", "stapler", "pencil", "tape", "scissors"]

	def set_dictionary(self, dictionary):
		self.dictionary = dictionary
		self.words = ["fur", "nigeria", "disco", "chewing gum", "cigar", "gamecube", "flower", "mp3", "bottle", "film", "radio", "knob", "fuck", "temperature", "milk", "mouse", "man", "wax", "pillow", "bicycle", "pub", "telephone", "stalk", "dog", "cat", "blacksmith", "glass", "door", "house", "metal", "lighter", "window", "mechanic", "camera", "stapler", "pencil", "tape", "scissors"]

	def on_tick(self, bot, time):
		self.time = time
		
		if self.running and (not self.timeout or time > self.timeout):
			if self.timeout and time - self.timeout > datetime.timedelta(0, 0, 0, 0, 10): #if we're 10 minutes it's more than just lag...
				self.running = False
				return

			self.timeout_streak += 1
			if self.timeout_streak > 3:
				self.timeout_streak = 0
				self.send_timeout(bot)
				self.send_timeout_quit(bot)
				self.stop(bot)
			else:
				if self.current_question:
					self.send_timeout(bot)
				self.new_question()
				self.send_question(bot)

	def on_privmsg(self, bot, source, target, message):
		self.on_tick(bot, self.time)

		if self.running:
			if self.current_question[1] == message:
				self.timeout_streak = 0

				if source in self.players:
					self.players[source] += 1
				else:
					self.players[source] = 1

				bot.tell(self.name, "Yay! %s got it!" % utility.extract_nick(source))

				self.new_question()
				self.send_question(bot)

	def start(self, bot):
		if not self.running:
			self.running = True
			self.current_question = None
			self.timeout = None
			bot.tell(self.name, "Game started.")

	def new_question(self):
		if len(self.words):
			word = self.words[0]
			self.words = self.words[1:]

			question = standard.WikipediaCommand.instance.wp_get(word)

			if question:
				question = re.sub("(?i)" + word, "*" * len(word), question)  
				self.current_question = (question, word)
		
		if not self.current_question:
			self.current_question = random.choice(self.dictionary.items())

		self.timeout = self.time + datetime.timedelta(0, 30)

	def send_question(self, bot):
		bot.tell(self.name, "Question: %s" % self.current_question[0])

	def stop(self, bot):
		if self.running:
			self.running = False
			bot.tell(self.name, "Game stopped.")

	def format_hiscore(self, tuple):
		return "%s: %d" % (utility.extract_nick(tuple[0]), tuple[1])

	def send_hiscore(self, bot):
		l = self.players.items()
		l.sort(key=lambda x: (x[1], x[0]))
		str = ", ".join(map(self.format_hiscore, reversed(l)))
		bot.tell(self.name, "Hi-score: %s." % str)

	def send_timeout(self, bot):
		bot.tell(self.name, "Timed out. Answer: %s." % self.current_question[1])

	def send_timeout_quit(self, bot):
		bot.tell(self.name, "Stopping inactive game.")

class GamePlugin(Command):
	hooks = ['on_privmsg']   

	def __init__(self):
		self.dictionary = { "*round time machine*": "clock", "*fourlegged reliever*": "chair", "*round rubber carrier*": "wheel", "*code machine*": "matricks", "*italian plumber*": "mario", "*squishy ball with gun*": "tee", "*round house kick master*": "chuck norris", "*best encoding*": "utf-8" }
		self.games = {}

	def on_load(self):
		self.load_games()
	
		for game in self.games.values():
			game.set_dictionary(self.dictionary)

	def on_unload(self):
		self.save_games()

	def on_save(self):
		self.save_games()

	def save_games(self):
		file = open('data/games.txt', 'w')
		p = pickle.Pickler(file)
		p.dump(self.games)
		file.close()

	def load_games(self):
		try:
			with open('data/games.txt', 'r') as file:
				self.games = pickle.Unpickler(file).load()
		except:
			pass


	def trig_gamestart(self, bot, source, target, trigger, argument):
		if not target in self.games.keys():
			self.games[target] = Game(target)
			self.games[target].set_dictionary(self.dictionary)
	
		game = self.games[target]
		game.start(bot)

	def trig_gamestop(self, bot, source, target, trigger, argument):
		if target in self.games.keys():
			game = self.games[target]
			game.stop(bot)

			self.on_save()
	
	def trig_gamehiscore(self, bot, source, target, trigger, argument):
		if target in self.games.keys():
			game = self.games[target]
			game.send_hiscore(bot)
		else:
			return "I have no hiscore for this game."

	def on_privmsg(self, bot, source, target, message):
		if target in self.games.keys():
			game = self.games[target]
			game.on_privmsg(bot, source, target, message)

		return None

	def timer_beat(self, bot, time):
		for game in self.games.values():
			game.on_tick(bot, time)
