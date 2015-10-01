# -*- coding: utf-8 -*-

import json
import utility
from commands import Command

class Metacritic(Command):
    def trig_metacritic(self, bot, source, target, trigger, argument):
        """Command used to search the review aggregation site Metacritic.com"""
        return self._run_command(argument.strip()).encode('utf-8')

    def trig_mc(self, bot, source, target, trigger, argument):
        """Shorthand for command metacritic"""
        return self.trig_metacritic(bot, source, target, trigger, argument)

    USAGE = u"Usage: .metacritic <title>"

    URL_BASE = 'http://www.metacritic.com'
    URL_API = URL_BASE + '/autosearch'
    URL_MANUAL_SEARCH = URL_BASE + '/search/all/%s/results'

    def __init__(self):
        pass

    def _run_command(self, search_term):
        if not search_term:
            return self.USAGE

        raw_result = self._get_raw_result(search_term)
        if not raw_result:
            return u"Could not retrieve data from Metacritic :("

        decoded_result = json.loads(raw_result['data'])
        items = decoded_result['autoComplete']

        if len(items) == 0:
            return u"No item found. Manual search: " + self._manual_search_url(search_term)
        else:
            return self._formatted_search_result(items[0], search_term)

    def _get_raw_result(self, search_term):
        headers = {'X-Requested-With': 'XMLHttpRequest',
                   'Referer': self.URL_BASE}
        post_data = {'search_term': search_term}

        return utility.read_url(self.URL_API, headers, post_data)

    def _manual_search_url(self, search_term):
        return self.URL_MANUAL_SEARCH % utility.escape(search_term)

    def _formatted_search_result(self, item, search_term):
        template = u"{name} ({formatted_info}), {formatted_score}, {item_url}" + \
            u" | All results: {manual_search_url}"

        data = {'name': item['name'],
                'formatted_info': self._formatted_item_info(item),
                'formatted_score': self._formatted_item_score(item),
                'item_url': self.URL_BASE + item['url'],
                'manual_search_url': self._manual_search_url(search_term)}

        return template.format(**data)

    def _formatted_item_info(self, item):
        result = u"%s" % item['refType']

        if item['itemDate']:
            result += u", %s" % str(item['itemDate'])

        return result

    def _formatted_item_score(self, item):
        if item['metaScore']:
            result = u"%s/100" % str(item['metaScore'])
        else:
            result = u"No score"

        if item['scoreWord']:
            result += u" (%s)" % item['scoreWord']

        return result
