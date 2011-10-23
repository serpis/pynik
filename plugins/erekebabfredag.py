# coding: utf-8

from commands import Command
import utility
import re

class erekebabfredag(Command):
    def __init__(self):
        pass

    def trig_erekebabfredag(self, bot, source, target, trigger, argument):
        url = 'http://ere.kebabfredag.nu'
        response = utility.read_url(url)
        data = response["data"]

        is_it = re.search(r'<h3>(.+)</h3>', data, re.S)
        if is_it:
            return is_it.group(1)               
        else:
            return 'Scrapping failed'                

