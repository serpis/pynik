# -*- coding: utf-8 -*-

# Plugin created by diggidanne

from commands import Command
from simplejson import loads
import utility
from datetime import date

class GitHub(Command):

    def __init__(self):
        # Setup action handlers
        self.action = {'lastcommit': self.lastcommit,
                       'pulls': self.pullrequests}

    def usage(self):
        return '.github [action] [repo]'

    def trig_github(self, bot, source, target, trigger, argument):
        args = argument.split(" ")
        if len(args) != 2:
            return self.usage()
        action = args[0]
        repo = args[1]
        if not self.action.has_key(action):
            return "I don't know how to do that"
        return self.action[action](repo)

    def lastcommit(self, repourl):
        fullurl = 'https://api.github.com/repos/%s/commits' % repourl
        response = utility.read_url(fullurl)

        json = loads(response['data'])
        message = json[0]['commit']['message']
        author = json[0]['author']['login']
        time = json[0]['commit']['author']['date']
        return "'%s' by %s, %s" % (message, author, self.prettify_date(time))

    def pullrequests(self, repourl):
        fullurl = 'https://api.github.com/repos/%s/pulls' % repourl
        response = utility.read_url(fullurl)

        json = loads(response['data'])
        return '%s has %s pull request(s)' % (repourl, len(json))

    def prettify_date(self, date_string):
        timepoints = {0: 'today',
                      1: 'yesterday',
                      2: 'two days ago',
                      3: 'three days ago',
                      4: 'four days ago',
                      5: 'five days ago',
                      6: 'six days ago'}
        today = date.today()
        commit_date = date(*[int(x) for x in date_string.split('T')[0].split('-')])
        days_diff = (today - commit_date).days
        if timepoints.has_key(days_diff):
            return timepoints[days_diff]
        # round to weeks
        return '%d weeks ago' % ((days_diff+1)/7)
        
