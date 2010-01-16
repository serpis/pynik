# coding: utf-8

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
            # serp commented this out due to spam annoyance
			#print 'GetQuote'
            self.NormalizePlays()
            DueQuotes = self.GetDueQuotes()
            if DueQuotes:
                chosenQuote = random.choice(DueQuotes)
                self.quotes[chosenQuote.index].played += 1
                   
                output = '#%s: %s' % (self.quotes[chosenQuote.index].index, self.quotes[chosenQuote.index].quote)
                #output = "choosing #%s out of %s quotes: %s (played %s times)" % (chosenQuote.index, len(DueQuotes), chosenQuote.quote, chosenQuote.played)
                self.SavePlaylist()
                return output
            # serp commented this out due to spam annoyance
			#else:
            #    print "emtpy list"

    def NormalizePlays(self):
        plays = []

        for quote in self.quotes:
            plays.append(quote.played)
        minplays = int(min(plays))
        if minplays != 0:
           for quote in self.quotes:
               quote.played = int(quote.played) - int(minplays)

    def GetDueQuotes(self):
		# serp commented this out due to spam annoyance
        #for quote in self.quotes:
        #    print quote.played

        DueQuotes = []
        for quote in self.quotes:
            if quote.played == 0:
                DueQuotes.append(quote)
        return DueQuotes;

    def LoadFromFiles(self):
		try:
			indexCounter = 0
			playlistfile = open(self.playlistfilename, 'r') 
			with open(self.quotefilename, 'r') as quotefile:
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
		except:
			# this empty except block should be shot and killed.
			pass

    def SaveQuotes(self):
        quotefile = open(self.quotefilename, "w")
        quotesToWrite = []

        for quote in self.quotes:
            quotesToWrite.append(quote.quote + "\n")

        quotefile.writelines(quotesToWrite)
        quotefile.close()

    def SavePlaylist(self):
        playlistToWrite = [] 
        playlistfile = open(self.playlistfilename, "w")

        for quote in self.quotes:
            playlistToWrite.append(str(quote.played) + "\n")

        playlistfile.writelines(playlistToWrite)
        playlistfile.close()

class QuoteCommand(Command):
    collection = QuoteCollection()

    def __init__(self):
        pass

    def trig_qotd(self, bot, source, target, trigger, argument):
        return self.collection.GetQuote()
