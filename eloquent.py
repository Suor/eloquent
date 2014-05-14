# -*- coding: utf-8 -*-
import re
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
        elif isinstance(other, (str, unicode)):
            return self + Const(other)
        else:
            return NotImplemented


class Matcher(object):
    def match(self, s, context=None):
        raise NotImplementedError

    def __add__(self, other):
        if isinstance(other, Matcher):
            return Pattern([self, other])
        elif isinstance(other, basestring):
            return Pattern([self, Const(other)])
        else:
            return NotImplemented

    def __radd__(self, other):
        if isinstance(other, basestring):
            return Pattern([Const(other), self])
        else:
            return NotImplemented

    def to_p(self):
        return Pattern([self])


class Const(Matcher):
    def __init__(self, const):
        self.const = const

    def __repr__(self):
        return 'Const(%r)' % self.const

    def match(self, word):
        if word == self.const:
            return {}

class Regex(Matcher):
    def __init__(self, regex):
        self.regex = re.compile(regex)

    def match(self, word):
        if self.regex.search(word):
            return {}


class Mapping(Matcher):
    def __init__(self, name, mapping, transform=lambda s: s.lower()):
        self.name = name
        self.mapping = {transform(k): v for k, v in mapping.items()}
        self.transform = transform

    def match(self, word, context=None):
        key = self.transform(word)
        if key in self.mapping:
            return {self.name: self.mapping[key]}

def CSMapping(name, mapping):
    return Mapping(name, mapping, transform=identity)

def Keyword(name, words, transform=lambda s: s.lower()):
    mapping = {w: w for w in words}
    return Mapping(name, mapping, transform=transform)

def CSKeyword(name, words):
    return Keyword(name, words, transform=identity)


class Int(Matcher):
    def __init__(self, name, lower=None, upper=None):
        self.name = name
        self.lower = lower or float('-inf')
        self.upper = upper or float('inf')

    def match(self, word):
        value = silent(int)(word)
        if value and self.lower <= value <= self.upper:
            return {self.name: value}


brands = ['Toyota', 'BMW']
models = {'Corolla': 'Toyota Corolla'}

patterns = [
    Keyword('brand', brands) + Mapping('model', models),
    Keyword('brand', brands).to_p(),
    Mapping('model', models).to_p(),
    Regex(u'^(с|от)$') + Int('year__ge', 1900, 2014) + Regex(u'^г(ода?)?$'),
    Regex(u'^(по|до)$') + Int('year__le', 1900, 2014) + Regex(u'^г(ода?)?$'),
    Int('year', 1900, 2014) + Regex(u'^г(ода?)?$'),
    Int('year', 1900, 2014).to_p(),
]

import traceback, sys

def parse(s):
    # print >> sys.stderr, '=' * 100
    # traceback.print_stack()
    words = s.split()
    print 'words', words
    return some(p.match(words) for p in patterns)


# pattern matching in python syntax
# parser tries to match begining of a sentence against all the patterns:
#   - in order, take first success
#   - add scores, choose highest
#   - longest match? if no *+ then can be done in terms of 1
