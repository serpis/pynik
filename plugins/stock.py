from commands import Command

from urllib2 import Request, urlopen

""" mIRC style color codes """
GREEN = "\x033"
RED = "\x034"   
ENDC = "\x03"

class StockCommand(Command):
    usage = "Usage: .stock <ticker symbol>"

    def __init__(self):
        pass

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

        elems = csv_str.split(',')

        return dict(name=elems[0].strip('"'), ask_price=elems[1], change=elems[2], changep=elems[3].strip('"'))

    def trig_stock(self, bot, source, target, trigger, argument):
        """ Retreives some stock data for a given ticker symbol """

        ticker_symbol = argument.strip().split(' ', 1)[0]
        if not ticker_symbol:
            return self.usage

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

