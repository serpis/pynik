# -*- coding: utf-8 -*-

# Plugin created by Merola

import re
import json
import urllib
import utility
from commands import Command

class PrisjaktCommand(Command):
    def trig_prisjakt(self, bot, source, target, trigger, argument,
                      network=None, **kwargs):
        """Command used to search the Swedish price comparison web site
        www.prisjakt.nu"""
        return self.run_command(argument.strip()).encode('utf-8')

    USAGE = u"Usage: .prisjakt <product name> | .prisjakt <product page url>"

    URL_BASE = 'http://www.prisjakt.nu/'
    URL_API = URL_BASE + 'ajax/server.php?class=Search_Supersearch&method=search&skip_login=1' + \
            '&modes=product,book,raw&limit=1&q=%s'
    URL_SEARCH = URL_BASE + 'search.php?query=%s'

    PATTERN_ITEM_URL = re.compile(re.escape(URL_BASE) + \
                                  r'(bok|produkt).php\?\w+=\d+')
    PATTERN_ITEM_NAME = re.compile(r'<h1.*?>\s*(?:<a href=".+?">)?' + \
                                   r'(?P<name>.+?)(?:</a>)?\s*</h1>', re.M)
    PATTERN_ITEM_PRICE = re.compile(r'<span class="price">' + \
                                    r'(?P<price>\d+:-)</span>')

    UTF8_AAO_CHARACTERS = 'åäöÅÄÖ'
    UTF8_AAO_TO_LATIN1_MAP = {'å':'%E5',
                              'ä':'%E4',
                              'ö':'%F6',
                              'Å':'%C5',
                              'Ä':'%C4',
                              'Ö':'%D6'}

    def run_command(self, argument):
        if not argument:
            return u"Prisjakt | %s" % self.USAGE
        elif self.PATTERN_ITEM_URL.match(argument):
            return self.look_up_item(argument)
        else:
            return self.search_for_item(self.build_query_string(argument))

    def look_up_item(self, url):
        response = utility.read_url(url)
        data = response['data'].decode('latin-1').replace('&nbsp;', u"")
        name_match = self.PATTERN_ITEM_NAME.search(data)
        if not name_match:
            return u"Could not extract product info :("

        name = utility.unescape(name_match.group('name'), True)
        price_match = self.PATTERN_ITEM_PRICE.search(data)
        if price_match:
            price = price_match.group('price')
        else:
            price = u"???:-"

        return u"%s, %s" % (name, price)

    def build_query_string(self, argument):
        # We need to search in latin-1 encoding to get correct results,
        # i.e. encode 'ö' as %F6 instead of %C3B6, and so on.
        # This ugly workaround is used since pynik is not encoding-aware.
        query = urllib.quote_plus(argument, self.UTF8_AAO_CHARACTERS)

        for key in self.UTF8_AAO_TO_LATIN1_MAP.keys():
            query = query.replace(key, self.UTF8_AAO_TO_LATIN1_MAP[key])

        return query

    def search_for_item(self, query_string):
        json_result = utility.read_url(self.URL_API % query_string)
        if not json_result:
            return u"Could not retrieve data from Prisjakt :("

        decoded_result = json.loads(json_result['data'])
        if decoded_result['error']:
            return u"Could not search Prisjakt: " + decoded_result['message']

        name, link, price = self.extract_product_name_link_and_price(decoded_result)
        if not name or not link:
            return u"No product found. | Manual search: " + \
                    self.URL_SEARCH % query_string
        elif not price:
            price = u"???:-"

        return u"%s, %s, %s | All results: %s" % \
                (name, price, link, self.URL_SEARCH % query_string)

    def extract_product_name_link_and_price(self, search_result):
        item = {}

        for category in ['product', 'book', 'raw']:
            items = search_result['message'][category]['items']
            if len(items) > 0:
                item = items[0]
                break

        name = item.get('name', None)
        link = item.get('url', None)

        raw_price = item.get('price', {})
        if isinstance(raw_price, (int, long)):
            price = u"%d:-" % raw_price
        else:
            price = raw_price.get('display', None)

        return (name, link, price)
