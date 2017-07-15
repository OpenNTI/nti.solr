#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.common.string import is_true

from nti.contentsearch.interfaces import ISearchQuery

from nti.solr import _OR_
from nti.solr import _AND_

from nti.solr.interfaces import ISOLRQueryTerm
from nti.solr.interfaces import ISOLRFilterQuery
from nti.solr.interfaces import ISOLRQueryParams
from nti.solr.interfaces import ISOLRQueryValidator

from nti.solr.lucene import is_valid_query


@interface.implementer(ISOLRQueryValidator)
class _SOLRQueryValidator(object):

    def __init__(self, *args):
        pass

    def validate(self, query):
        query = ISearchQuery(query)
        if not is_valid_query(query.term):
            raise AssertionError("Invalid query %s" % query.term)


class TermMixin(object):

    def __init__(self):
        self._terms = dict()

    def add_term(self, name, value):
        self._terms[name] = value

    def __contains__(self, *args, **kwargs):
        return self._terms.__contains__(*args, **kwargs)

    def __iadd__(self, other):
        self._terms.update(other._terms)
        return self


@interface.implementer(ISOLRQueryTerm)
class QueryTerm(TermMixin):

    default = None

    def to_solr(self, op=_OR_):
        if self.default:
            return self.default
        return op.join(u'%s:(%s)' % (name, value)
                       for name, value in self._terms.items())

    def __iadd__(self, other):
        if other.default:
            self.default = other.default
        self._terms.update(other._terms)
        return self


@interface.implementer(ISOLRFilterQuery)
class FilterQuery(TermMixin):

    def __init__(self):
        super(FilterQuery, self).__init__()
        self._or_list = dict()
        self._and_list = dict()

    def add_or(self, name, values):
        self._or_list.setdefault(name, set())
        self._or_list[name].update(values)

    def add_and(self, name, values):
        self._and_list.setdefault(name, set())
        self._and_list[name].update(values)

    def to_solr(self, op=_AND_):
        result = dict(self._terms)
        for name, values in self._or_list.items():
            result[name] = u"(%s)" % _OR_.join(values)
        for name, values in self._and_list.items():
            result[name] = u"(%s)" % _AND_.join(values)
        result = (u'%s:%s' % (name, value) for name, value in result.items())
        return op.join(result)

    def __contains__(self, *args, **kwargs):
        return self._terms.__contains__(*args, **kwargs) \
            or self._or_list.__contains__(*args, **kwargs) \
            or self._and_list.__contains__(*args, **kwargs)

    def __iadd__(self, other):
        self._terms.update(other._terms)
        for name, values in other._or_list.items():
            self.add_or(name, values)
        for name, values in other._and_list.items():
            self.add_and(name, values)
        return self


@interface.implementer(ISOLRQueryParams)
class QueryParms(dict):

    list_fields = ('fl', 'hl.fl')

    def __iadd__(self, other):
        temp = {}
        for name in self.list_fields:
            values = other.get(name)
            if values:
                own = set(self.pop(name) or ())
                own.update(values)
                temp[name] = list(own)
        # update list fields
        self.update(temp)
        for name, value in other.items():
            if name not in self.list_fields:
                # destruct previous
                self[name] = value
        return self

    def to_solr(self):
        result = dict(self)
        for name in self.list_fields:
            values = result.get(name)
            if values:
                result[name] = u','.join(values)
        return result


def prepare_solr_query(term, fq, params, cache=False):
    term = term.to_solr()
    fq_query = fq.to_solr()
    if fq_query:
        if not cache or 'fq' in params:
            term = u"((%s)%s(%s))" % (term, _AND_, fq_query)
        else:
            params['fq'] = fq_query
    return term, params


def prepare_solr_triplets(triplets):
    terms = []
    params = None
    cache = len(triplets) == 1
    for count, triplet in enumerate(triplets):
        term, fq, t_params = triplet
        if count:
            params += t_params
        else:
            params = t_params
        term, params = prepare_solr_query(term, fq, params, cache)
        terms.append(term)
    term = _OR_.join(terms)
    return term, params


def hl_useFastVectorHighlighter(query):
    query = ISearchQuery(query)
    context = query.context or {}
    vector = context.get('hl.useFastVectorHighlighter') \
          or context.get('useFastVectorHighlighter')
    return is_true(vector)


def hl_snippets(query):
    query = ISearchQuery(query)
    context = query.context or {}
    snippets = context.get('hl.snippets') or context.get('snippets')
    return str(snippets) if snippets else '2'


def hl_useSimpleEncoder(query):
    query = ISearchQuery(query)
    context = query.context or {}
    encoder = context.get('hl.encoder') or context.get('encoder')
    return 'simple' == encoder


def search_fields(query, all_fields=()):
    # result = ()
    # TODO: Parse fields
    query = ISearchQuery(query)
    return all_fields


def hl_useHTMLEncoder(query):
    return not hl_useSimpleEncoder(query)


def hl_removeEncodedHTML(query):
    query = ISearchQuery(query)
    context = query.context or {}
    removed = context.get('hl.removeEncoded') or context.get('removeEncoded')
    return not removed or is_true(removed)  # true by default
