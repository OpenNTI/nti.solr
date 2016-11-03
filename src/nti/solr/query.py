#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.contentsearch.interfaces import ISearchQuery

from nti.solr.interfaces import ISOLRQueryValidator

from nti.solr.lucene import is_valid_query

@interface.implementer(ISOLRQueryValidator)
class _SOLRQueryValidator(object):
	
	def __init__(self, *args):
		pass
	
	def validate(self, query):
		query = ISearchQuery(query)
		return is_valid_query(query.term)
