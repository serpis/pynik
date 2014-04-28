from commands import Command
import utility

import re
from urllib2 import Request, urlopen

""" mIRC style color codes """
GREEN = "\x033"
RED = "\x034"   
ENDC = "\x03"

class StockCommand(Command):
    usage = "Usage: .stock <ticker symbol>"

    def __init__(self):
        self.__aliases = {}
        self.__yahoo_exp = re.compile("^\"(?P<name>.+)\",(?P<ask_price>.+),(?P<change>.+),\"(?P<changep>.+)\"$")
        self.__stock_exp = re.compile("^(\^?[a-zA-Z0-9\.\-]+)$")
        self.__alias_exp = re.compile("^([^\s]+)\s+(\^?[a-zA-Z0-9\.\-]+)$")

    def __get(self, ticker_symbol):
        """ Requests a CSV file with the data from Yahoo Finance """

        # n = name
        # l1 = last trade
        # c1 = change
        # p2 = change percent
        url = "http://finance.yahoo.com/d/quotes.csv?s=%s&f=nl1c1p2" % ticker_symbol
        req = Request(url)
        resp = urlopen(req) 
        csv_str = resp.read().decode().strip()

        m = self.__yahoo_exp.match(csv_str)

        return m.groupdict()

    def trig_stock(self, bot, source, target, trigger, argument):
        """ Retreives some stock data for a given ticker symbol """

        m = self.__stock_exp.match(argument)
        if not m:
            return self.usage

        if self.__aliases.has_key(m.group(1)):
            ticker_symbol = self.__aliases[m.group(1)]
        else:
            ticker_symbol = m.group(1)

        try:
            data = self.__get(ticker_symbol)
        except:
            return "Couldn't get data from Yahoo Finance! Sorry!"

        if "N/A" in data.values():
            return "That wasn't a real ticker symbol, was it?"

        if data["change"].startswith('+'):
            return data["name"] + " " + data["ask_price"] + " " + \
                   GREEN + data["change"] + " " + data["changep"] + ENDC
        elif data["change"].startswith('-'):
            return data["name"] + " " + data["ask_price"] + " " + \
                   RED + data["change"] + " " + data["changep"] + ENDC
        else:
            return data["name"] + " " + data["ask_price"] + " " + \
                   data["change"] + " " + data["changep"] 

    def trig_stockalias(self, bot, source, target, trigger, argument):
        """ Allows users to add an easy to remember alias for their dividend champ! """

        m = self.__alias_exp.match(argument)
        
        if not m:
            return "Syntax: stockalias <alias> <ticker symbol>"

        alias, ticker_symbol = m.group(1, 2)
        
        # Make sure no one turns a real ticker symbol into an alias for something else
        try:
            data = self.__get(alias)
        except:
            return "Couldn't sanity check that with Yahoo Finance! No deal!"

        if not "N/A" in data.values():
            return "Nice try."

        self.__aliases[alias] = ticker_symbol 
        self.save()

        return "Alias %s added." % alias 

    def save(self):
        utility.save_data("stockaliases", self.__aliases)

    def on_modified_options(self):
        self.save()

    def on_load(self):
        self.__aliases = utility.load_data("stockaliases", {})

    def on_unload(self):
        self.__aliases.clear()

