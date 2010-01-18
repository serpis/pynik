# coding: utf-8

__author__ = 'Simon Pantzare'

from commands import Command

import popen2
from string import punctuation
from difflib import get_close_matches, SequenceMatcher
from random import sample

def normalize(sentence):
    sentence = sentence.strip()
    if len(sentence) == 0:
        return ''

    normd = sentence
    ends = ['.', '!', '?']
    for end in ends:
        parts = normd.split(end)
        j = end + ' '
        normd = j.join([part.capitalize() for part in parts])
    normd = normd.strip()

    if not normd[-1] in ends:
        return normd + '.'
    return normd


def _garbage(word):
    need = len(word)
    return ''.join(sample(punctuation * need, need)).replace(' ', '')


class Speller(object):
    """
    **NOTE:** Parts based on
              http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/117221 .
    """

    def __init__(self, lang='en'):
        self._f = popen2.Popen3("aspell -l %s --run-together --run-together-min=3 -a" % lang)
        self._f.fromchild.readline()

    def spell(self, word):
        if word in punctuation:
            return word

        self._f.tochild.write(word+'\n')
        self._f.tochild.flush()
        s = self._f.fromchild.readline().strip()
        self._f.fromchild.readline()

        if len(s) == 0:
            return _garbage(word)
        else:
            if s[0] == '*' or s[0] == '-':
                return word
            elif s[0] == '&':
                sugs = s[s.find(':')+2:].split(', ')
                good = get_close_matches(word, sugs)
                if len(good) == 0:
                    # No match was good, return one at random.
                    return sample(sugs, 1)[0]
                else:
                    return good[0]
            else:
                # Aspell was unable to find a remotely similar valid word. Return
                # garbage.
                return _garbage(word)

    def make_perfect(self, sentence):
        lower = sentence.lower()
        perfect_sentence = []
        for token in lower.split():
            perfect_sentence.append(self.spell(token))
        perfect_sentence = ' '.join(perfect_sentence)
        return normalize(perfect_sentence)


class stava(Command):
    def __init__(self):
        self.speller = Speller(lang='sv')
        self.matcher = SequenceMatcher()

    def trig_stava(self, bot, source, target, trigger, argument):
        sentence = argument.strip()
        if len(sentence) == 0:
            return "Ge mig en mening eller ett ord som jag ska stava!"

        if len(sentence.split()) == 1:
            perfect = self.speller.spell(sentence)
        else:
            perfect = self.speller.make_perfect(sentence)

        self.matcher.set_seqs(sentence, perfect)
        sim = self.matcher.ratio()
        if sim == 1.0:
            return "Korrekt!"
        return "%i%% rätt, du menade: %s" % (sim * 100.0, perfect)

