# coding: utf-8

from commands import Command
import utility
import re
import json

class erekebabfredag(Command):
    def __init__(self):
        pass

    def trig_erekebabfredag(self, bot, source, target, trigger, argument):
        url = 'http://ere.kebabfredag.nu/api/erekebabfredag?format=json'
        response = utility.read_url(url)
        data = response["data"]
        jsondata = json.loads(data)

        if jsondata['isIt']:
            return u'Japp!'
        else:
            return u'Nepp :('
