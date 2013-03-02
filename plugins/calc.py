# -*- coding: utf-8 -*-

# Plugin created by Merola

import re
import json
import utility
from commands import Command

class CalculatorCommand(Command):
    def trig_calc(self, bot, source, target, trigger, argument,
                  network=None, **kwargs):
        """Calculator with support for unit and currency conversion,
        powered by Google"""
        return self.run_command(argument.strip()).encode('utf-8')
    
    USAGE = u"Usage: .calc <expression>"
    
    URL_API = 'http://www.google.com/ig/calculator?oe=utf-8&q=%s'
    URL_SEARCH = 'https://www.google.com/search?q=%s'
    
    PATTERN_LAZY_JSON = re.compile(r'(?<=[\{,])(\w+)(?=: )')
    PATTERN_HEX_CHAR = re.compile(r'\\x(?P<value>\w{2})')
    
    def run_command(self, argument):
        if not argument:
            return self.USAGE
        
        query_string = utility.escape(argument)
        result = self.calculate(query_string)
        manual_search = self.URL_SEARCH % query_string
        
        if result['error']:
            return u"Invalid input :S | Google search: %s" % manual_search
        
        left = result.get('lhs', u"?")
        right = result.get('rhs', u"?")
        output = u"%s = %s | %s" % (left, right, manual_search)
        return self.adapt_tags(output)
    
    def calculate(self, query):
        request = self.URL_API % query

        lazy_json_response = utility.read_url(request)['data'].decode('utf-8')
        strict_json_response = self.lazy_to_strict_json(lazy_json_response)
        unescaped_json_response = self.unescape_response(strict_json_response)
        response = json.loads(unescaped_json_response)
        
        if response['error'] == '0':
            response['error'] = ''
        
        return response
    
    def lazy_to_strict_json(self, lazy_json):
        """Adds quotes around unquoted identifiers in the JSON response."""
        return self.PATTERN_LAZY_JSON.sub(r'"\1"', lazy_json)
    
    def unescape_response(self, response):
        """Unescapes hex characters (e.g. \xab) and HTML entities."""
        response = self.PATTERN_HEX_CHAR.sub(self.unescape_hex_helper, response)
        return utility.unescape(response, True)
    
    def unescape_hex_helper(self, m):
        return unichr(int(m.group('value'), 16))
    
    def adapt_tags(self, text):
        """Converts HTML tags to IRC-friendly plaintext formatting."""
        return text.replace('<sup>', u"^(").replace('</sup>', u")")
