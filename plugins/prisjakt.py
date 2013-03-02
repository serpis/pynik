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
    URL_API = URL_BASE + 'ajax/jsonajaxserver.php?m=super_search&p=' + \
            '{"mode":"prod_pj","search":"%s","limit":1,"v4":1}'
    URL_SEARCH = URL_BASE + 'search.php?query=%s'
    
    PATTERN_ITEM_URL = re.compile(re.escape(URL_BASE) + \
                                  r'(bok|produkt).php\?\w+=\d+')
    PATTERN_ITEM_NAME = re.compile(r'<h1.*?>\s*(?:<a href=".+?">)?' + \
                                   r'(?P<name>.+?)(?:</a>)?\s*</h1>', re.M)
    PATTERN_ITEM_PRICE = re.compile(r'<span class="price">' + \
                                    r'(?P<price>\d+:-)</span>')
    PATTERN_SEARCH_NAME_AND_LINK = re.compile(r'<a.+?href="/' + \
                                              r'(?P<link>\w+\.php\?(?:p|e_id)=\d+)' + \
                                              r'".+?(?:js-popup|\n.+?expert)' + \
                                              r'.+?>.*\n(?:<img.+?>)?' + \
                                              r'\s*(?P<name>.+?)\s*\n</a>')
    PATTERN_SEARCH_PRICE = re.compile(r'<span class="price">' + \
                                      r'(?P<price>\d+:-)</span>')
    PATTERN_WHITESPACE = re.compile(r'\s+')
    
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
        json_result = self.run_item_search_query(query_string)
        if not json_result:
            return u"Could not retrieve data from Prisjakt :("
        
        html_result = self.extract_search_hit_html(json_result)
        if not html_result:
            return u"No product found. | Manual search: " + \
                    self.URL_SEARCH % query_string
        
        name, link, price = self.extract_product_name_link_and_price(html_result)
        if not name or not link:
            return u"No information found. | Manual search: " + \
                    self.URL_SEARCH % query_string
        elif not price:
            price = u"???:-"
        
        return u"%s, %s, %s | All results: %s" % \
                (name, price, link, self.URL_SEARCH % query_string)
    
    def run_item_search_query(self, query_string):
        """Runs a search query, returns the JSON search result."""
        response = utility.read_url(self.URL_API % query_string)
        response_lines = response['data'].split('\n')
        
        # The JSON payload is on the second line
        if len(response_lines) >= 2:
            return response_lines[1]
        else:
            return None
    
    def extract_search_hit_html(self, json_result):
        """Extracts the first search hit from the JSON search result."""
        query_result = json.loads(json_result)['result']
        if query_result['count'] > 0:
            return query_result['html'].replace('&nbsp;', '')
        else:
            return None
    
    def extract_product_name_link_and_price(self, html):
        """Parses search hit HTML, returns product data."""
        name_and_link_match = self.PATTERN_SEARCH_NAME_AND_LINK.search(html)
        price_match = self.PATTERN_SEARCH_PRICE.search(html)
        
        if not name_and_link_match:
            return (None, None, None)
        
        name = self.clean_up_product_name(name_and_link_match.group('name'))
        link = self.URL_BASE + name_and_link_match.group('link')
        if price_match:
            return (name, link, price_match.group('price'))
        else:
            return (name, link, None)
    
    def clean_up_product_name(self, name):
        """Removes HTML tags and extra whitespace from product name."""
        name = name.replace('<span class="search_hit">', u"")
        name = name.replace('</span>', u"")
        return re.sub(self.PATTERN_WHITESPACE, u" ", name)
