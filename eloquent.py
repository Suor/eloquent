# -*- coding: utf-8 -*-
import re
from collections import defaultdict, Counter
from itertools import product

from funcy import *


class Pattern(list):
    def match(self, words):
        if len(words) < len(self):
            return False

        matches = (m.match(word) for m, word in zip(self, words))
        matched = list(takewhile(notnone, matches))
        print self, words
        print matched, len(matched), len(self), join(matched)
        if len(matched) == len(self):
            return join(matched)

    @staticmethod
    def guess_matcher(value):
        if isinstance(value, Matcher):
            return value
        elif isinstance(value, (str, unicode)):
            return Regex(value)
        else:
            raise NotImplementedError

    def __add__(self, other):
        return Pattern(self[:] + [self.guess_matcher(other)])

    def __radd__(self, other):
        return Pattern([self.guess_matcher(other)] + self[:])


class Matcher(object):
    def match(self, s, context=None):
        raise NotImplementedError

    def __add__(self, other):
        return Pattern([self]) + other

    def __radd__(self, other):
        return other + Pattern([self])

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

    def __repr__(self):
        return 'Regex(%r)' % self.regex.pattern

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

def Keyword(name, words, aliases={}, transform=lambda s: s.lower()):
    mapping = {w: w for w in words}
    mapping.update(aliases)
    return Mapping(name, mapping, transform=transform)

def CSKeyword(name, words, aliases={}):
    return Keyword(name, words, aliases=aliases, transform=identity)


class FuzzyKeywords(Matcher):
    extract_features = raiser(NotImplementedError)

    def __init__(self, name, mapping, transform=lambda s: s.lower()):
        self.name = name
        self.transform = transform
        self.mapping = {transform(k): v for k, v in mapping.items()}
        self.words_by_feature = group_by_keys(self.extract_features, self.mapping)

    def match(self, word):
        features = self.extract_features(self.transform(word))
        counter = Counter(icat(ikeep(self.words_by_feature.get, features)))
        top = counter.most_common(1)
        if top:
            return {self.name: self.mapping[top[0][0]]}

class Misspelled(FuzzyKeywords):
    """Spell checker based on triplets"""
    extract_features = partial(partition, 3, 1)

class Translit(FuzzyKeywords):
    en_to_ru = {
        'a': (u'а',),
        'b': (u'б',),
        'c': (u'с', u'ц', u'к'),
        'd': (u'д',),
        'e': (u'е',),
        'f': (u'ф',),
        'g': (u'г', u'ж'),
        'h': (u'х',),
        'i': (u'и', u'й'),
        'k': (u'к',),
        'l': (u'л',),
        'm': (u'м',),
        'n': (u'н',),
        'o': (u'о',),
        'p': (u'п',),
        'q': (u'к',),
        'r': (u'р',),
        's': (u'с',),
        't': (u'т',),
        'u': (u'у', u'ю'),
        'v': (u'в',),
        'w': (u'в', u'у'),
        'x': (u'кс', u'х',),
        'y': (u'й',),
        'z': (u'з',),
    }

    @classmethod
    def extract_features(cls, word):
        letter_variants = (cls.en_to_ru.get(c, c) for c in word)
        return map(u''.join, product(*letter_variants))


class Int(Matcher):
    def __init__(self, name, lower=None, upper=None):
        self.name = name
        self.lower = lower or float('-inf')
        self.upper = upper or float('inf')

    def match(self, word):
        value = silent(int)(word)
        if value and self.lower <= value <= self.upper:
            return {self.name: value}


# Domain data
brands = ['Toyota', 'BMW']
brand_aliases = {u'бумер': 'BMW'}
models = {'Corolla': 'Toyota Corolla'}

brand_dict = merge({b: b for b in brands}, brand_aliases)

# Construct matchers
brand = Keyword('brand', brands, aliases=brand_aliases)
model = Mapping('model', models)
year = Int('year', 1900, 2014)
year_ge = Int('year__ge', 1900, 2014)
year_le = Int('year__le', 1900, 2014)

patterns = [
    brand + model,
    brand.to_p(),
    model.to_p(),
    u'^(с|от)$' + year_ge + u'^г(ода?)?$',
    u'^(с|от)$' + year_ge,
    u'^(по|до)$' + year_le + u'^г(ода?)?$',
    u'^(по|до)$' + year_le,
    year + u'^г(ода?)?$',
    year.to_p(),
    Misspelled('brand', brand_dict).to_p(),
    Misspelled('model', models).to_p(),
    Translit('brand', brand_dict).to_p(),
    Translit('model', models).to_p(),
]

import traceback, sys


@print_calls
def parse(s):
    # print >> sys.stderr, '=' * 100
    # traceback.print_stack()
    words = s.split()
    # print 'words', words
    result = {}
    while words:
        for p in patterns:
            m = p.match(words)
            if m:
                result.update(m)
                words = words[len(p):]
                break
        else:
            break

    return result


# pattern matching in python syntax
# parser tries to match begining of a sentence against all the patterns:
#   - in order, take first success
#   - add scores, choose highest
#   - longest match? if no *+ then can be done in terms of 1
