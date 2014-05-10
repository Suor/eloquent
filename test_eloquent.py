# -*- coding: utf-8 -*-
# Names:
#   - future filter/search
#   - human query
#   - natural filter/query
#   - eloquent
# Aimed to enable natural language in filter/search forms.

# brand,
# model,
# year

from eloquent import parse

def test_keyword():
    assert parse(u'Hello') is None
    assert parse(u'Toyota') == {'brand': 'Toyota'}
    assert parse(u'Toyota Corolla') == {'brand': 'Toyota', 'model': 'Toyota Corolla'}

def test_orphan_keyword():
    assert parse(u'Corolla') == {'model': 'Toyota Corolla'}

def test_keyword_case():
    assert parse(u'toyota') == {'brand': 'Toyota'}
    assert parse(u'TOYOTA') == {'brand': 'Toyota'}
    assert parse(u'corolla') == {'model': 'Toyota Corolla'}
    assert parse(u'toyota corolla') == {'brand': 'Toyota', 'model': 'Toyota Corolla'}

# def test_translit_keyword():
#     assert parse(u'тойота') == {'brand': 'Toyota'}
#     assert parse(u'тойота королла') == {'brand': 'Toyota', 'model': 'Toyota Corolla'}
#     assert parse(u'королла') == {'model': 'Toyota Corolla'}

# def test_broken_keyword():
#     assert parse(u'corola') == {'model': 'Toyota Corolla'} # Mind single "l"

# def test_broken_translit_keyword():
#     assert parse(u'корола') == {'model': 'Toyota Corolla'} # Mind single "л"
#     assert parse(u'каролла') == {'model': 'Toyota Corolla'}
#     assert parse(u'карола') == {'model': 'Toyota Corolla'}
#     assert parse(u'тайота') == {'brand': 'Toyota'}
#     assert parse(u'таёта') == {'brand': 'Toyota'}

# def test_aliases():
#     assert parse(u'бумер') == {'brand': 'BMW'}
#     assert False # TODO: add more examples


def test_int_keyword():
    assert parse(u'2009 года') == {'year': 2009}
    assert parse(u'2010 г') == {'year': 2010}

def test_orphan_int():
    assert parse(u'2009') == {'year': 2009}

# def test_range():
#     assert parse(u'с 2009 по 2012 год') == {'year__range': (2009, 2012)}
#     assert parse(u'от 2009 до 2012 года') == {'year__range': (2009, 2012)}
    # assert parse(u'от 2009 до 2012 года') == {'year__range': (2009, 2012)}

# def test_orphan_range():
#     assert parse(u'от 2009 до 2012') == {'year__range': (2009, 2012)}
#     assert parse(u'2009-2012') == {'year__range': (2009, 2012)}

# def test_abbrev_range():
#     assert parse(u'2009-12') == {'year__range': (2009, 2012)}
#     assert parse(u'с 9 по 12') == {'year__range': (2009, 2012)}


def test_bound():
    assert parse(u'с 2009 года') == {'year__ge': 2009}
    assert parse(u'от 2009 года') == {'year__ge': 2009}
    assert parse(u'по 2012 года') == {'year__le': 2012}
    assert parse(u'до 2012 года') == {'year__le': 2012}

# def test_orphan_bound():
#     assert parse(u'от 2009') == {'year__ge': 2009}
#     assert parse(u'от 2009') == {'year__ge': 2009}
#     assert parse(u'по 2012') == {'year__le': 2012}
#     assert parse(u'до 2012') == {'year__le': 2012}

# def test_abbrev_bound():
#     assert False


# def test_rel_bound():
#     assert parse(u'не старше 3 лет') == {'year__ge': 2011} # now is 2014
#     assert False # TODO: add more examples

# def test_rel_range():
#     assert False
