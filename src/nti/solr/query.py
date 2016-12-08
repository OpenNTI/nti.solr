#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.common.string import is_true

from nti.contentsearch.interfaces import ISearchQuery

from nti.solr.interfaces import ISOLRQueryValidator

from nti.solr.lucene import is_valid_query

@interface.implementer(ISOLRQueryValidator)
class _SOLRQueryValidator(object):
	
	def __init__(self, *args):
		pass
	
	def validate(self, query):
		query = ISearchQuery(query)
		if not bool(is_valid_query(query.term)):
			raise AssertionError("Invalid query %s" % query.term)

def hl_useFastVectorHighlighter(query):
	query = ISearchQuery(query)
	context = query.context or  {}
	vector = 	context.get('hl.useFastVectorHighlighter') \
			or	context.get('useFastVectorHighlighter')
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

def hl_useHTMLEncoder(query):
	return not hl_useSimpleEncoder(query)

def hl_removeEncodedHTML(query):
	query = ISearchQuery(query)
	context = query.context or {}
	removed = context.get('hl.removeEncoded') or context.get('removeEncoded')
	return not removed or is_true(removed) # true by default
