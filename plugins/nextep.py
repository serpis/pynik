# -*- coding: utf-8 -*-

from commands import Command
import re
import utility

class NextEpisodeCommand(Command):
    def trig_nextep(self, bot, source, target, trigger, argument,
                    network=None, **kwargs):
        """Information about the latest and next episode of a TV show."""
        return self.run_command(argument.strip()).encode('utf-8')
    
    USAGE = u"Usage: .nextep <tv show name>"
    
    URL_API = 'http://services.tvrage.com/tools/quickinfo.php?show=%s'
    URL_SEARCH = 'http://tvrage.com/search.php?search=%s'
    
    PATTERN_DATA_ENTRY = re.compile(r'(?P<key>.+?)@(?P<value>.+)')

    def run_command(self, query_string):
        if not query_string:
            return self.USAGE
        
        query_string = utility.escape(query_string)
        
        info = self.fetch_show_info(query_string)
        name = info.get('Show Name')
        if not name:
            return u"TV show not found | Manual search: " + \
                    self.URL_SEARCH % query_string
        
        year = info.get('Premiered')
        if year and year not in name:
            name += u" (%s)" % year
        
        latest_ep = info.get('Latest Episode', u"Unknown")
        next_ep = info.get('Next Episode',
                           u"Unknown - %s" %
                           info.get('Status', u"Unknown status"))
        url = info.get('Show URL', self.URL_SEARCH % query_string)
        
        return u"%s | Latest: %s | Next: %s | Read more: %s" % \
                (name, latest_ep, next_ep, url)

    def fetch_show_info(self, show):
        info = {}
        query_result = utility.read_url(self.URL_API % show)
        raw_data = utility.unescape(query_result['data'].decode('utf-8'), True)
        for m in self.PATTERN_DATA_ENTRY.finditer(raw_data):
            info[m.group('key')] = m.group('value').replace('^', u", ")
        return info
