# -*- coding: utf-8 -*-
from funcy import *


class Pattern(list):
    def match(self, words):
        # if len(words) != len(self):
        #     return False
        matches = (m.match(word) for m, word in zip(self, words))
        matched = list(takewhile(notnone, matches))
        print self
        print matched, len(matched), len(self), join(matched)
        if len(matched) == len(self):
            return join(matched)

    def __add__(self, other):
        if isinstance(other, Matcher):
            p = Pattern(self)
            p.append(other)
            return p
        else:
            return NotImplemented


class Matcher(object):
    def match(self, s, context=None):
        raise NotImplementedError

    def __add__(self, other):
        if isinstance(other, Matcher):
            return Pattern([self, other])
        else:
            return NotImplemented

    def to_p(self):
        return Pattern([self])


class Keyword(Matcher):
    def __init__(self, name, variants):
        self.name = name
        self.variants = set(variants)

    def match(self, word, context=None):
        if word in self.variants:
            return {self.name: word}


class Mapping(Matcher):
    def __init__(self, name, mapping):
        self.name = name
        self.mapping = mapping

    def match(self, word, context=None):
        if word in self.mapping:
            return {self.name: self.mapping[word]}


patterns = [
    Keyword('brand', ['Toyota', 'BMW']).to_p(),
    Mapping('model', {'Corolla': 'Toyota Corolla'}).to_p(),
    # Int('year', 1900, 2014) + Const(u'года'),
]

def parse(s):
    words = s.split()
    return some(p.match(words) for p in patterns)


# pattern matching in python syntax
# parser tries to match begining of a sentence against all the patterns:
#   - in order, take first success
#   - add scores, choose highest
#   - longest match? if no *+ then can be done in terms of 1
