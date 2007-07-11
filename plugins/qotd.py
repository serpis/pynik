# coding: latin-1

from __future__ import with_statement
from commands import Command
import string, random

class quote:
	quote = ""
	index = 0
	played = 0

class QuoteCollection:
	quotes = []
	plays = []
	quotefilename = "data/quotes.txt"
	playlistfilename = "data/playlist.txt"
	
	def __init__(self):
		self.LoadFromFiles()
	
	def GetQuote(self):
			print 'GetQuote'
			self.NormalizePlays()
			DueQuotes = self.GetDueQuotes()
			if DueQuotes:
				chosen = random.choice(DueQuotes).index
				self.quotes[chosen].played += 1

				return self.quotes[chosen].quote
			else:
				print "emtpy list"

	def NormalizePlays(self):
		plays = []

		for quote in self.quotes:
			plays.append(quote.played)
		minplays = int(min(plays))
		if minplays != 0:
		   for quote in self.quotes:
			   quote.played = int(quote.played) - int(minplays)

	def GetDueQuotes(self):
		for quote in self.quotes:
			print quote.played

		DueQuotes = []
		for quote in self.quotes:
			if quote.played == 0:
				DueQuotes.append(quote)
		return DueQuotes;

	def LoadFromFiles(self):
		indexCounter = 0
		with open(self.quotefilename, 'r') as quotefile:
			with open(self.playlistfilename, 'r') as playlistfile:
				for line in quotefile:
					currentQuote = quote()
	
					currentQuote.quote = string.strip(line)
				  	played = playlistfile.readline()
				  	try:
						currentQuote.played = int(played)
				  	except:
						currentQuote.played = 0
				  	currentQuote.index = indexCounter
				  
					self.quotes.append(currentQuote)
					indexCounter += 1

	def SaveToFiles(self):
		quotefile = open(self.quotefilename, "w")
		playlistfile = open(self.playlistfilename, "w")
		quotesToWrite = []
		playlistToWrite = [] 
		for quote in self.quotes:
			quotesToWrite.append(quote.quote + "\n")
			playlistToWrite.append(str(quote.played) + "\n")
		
		quotefile.writelines(quotesToWrite)
		playlistfile.writelines(playlistToWrite)
		
		quotefile.close()
		playlistfile.close()



class QuoteCommand(Command):
	triggers = ['qotd']
	collection = QuoteCollection()

	def __init__(self):
		pass

	def on_trigger(self, bot, source, target, trigger, argument):
		self.on_qotd(bot, source, target, trigger, argument)

	def on_qotd(self, bot, source, target, trigger, argument):
		bot.tell(target, self.collection.GetQuote())
