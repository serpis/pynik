# coding: utf-8

import re
import urlparse

from commands import Command


def _find_google_result_url(message):
    m = re.search(r'https?://([^/]*\.)?[Gg][Oo][Oo][Gg][Ll][Ee]\.[^/]+/url\S+', message)
    if not m:
        return None
    url = m.group(0)
    query_string = urlparse.urlsplit(url).query
    query_dict = urlparse.parse_qs(query_string)
    if "url" in query_dict:
        return query_dict["url"][0]
    else:
        return None


class DegooglePlugin(Command):
    def __init__(self):
        self._last_url = None

    def on_privmsg(self, bot, source, target, message):
        url = _find_google_result_url(message)
        if url:
            self._last_url = url

    def trig_degoogle(self, bot, source, target, trigger, argument):
        if argument:
            url = _find_google_result_url(argument)
            if not url:
                return "The argument was not a Google result URL."
            else:
                return "de-Googled: " + url
        elif self._last_url:
            return "de-Googled: " + self._last_url
        else:
            return "Did not find any Google result URL."
