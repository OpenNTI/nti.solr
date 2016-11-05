#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from dolmen.builtins.interfaces import IDict

from zope import component
from zope import interface

from nti.common.string import to_unicode

from nti.contentsearch.interfaces import ISearchHit

from nti.contentsearch.search_hits import SearchHit

from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import INTIIDValue
from nti.solr.interfaces import IStringValue
from nti.solr.interfaces import ICreatorValue
from nti.solr.interfaces import IMimeTypeValue
from nti.solr.interfaces import IContainerIdValue
from nti.solr.interfaces import ILastModifiedValue

@component.adapter(basestring)
@interface.implementer(IStringValue)
class _StringValue(object):

	def __init__(self, context=None):
		self.context = context

	def lang(self, context):
		return 'en'

	def value(self, context=None):
		context = self.context if context is None else context
		return to_unicode(context) if context else None

HIT_FIELDS = ((INTIIDValue, 'NTIID'),
			  (ICreatorValue, 'Creator'),
			  (IMimeTypeValue, 'TargetMimeType'),
			  (IContainerIdValue, 'ContainerId'),
			  (ILastModifiedValue, 'lastModified'))

@interface.implementer(ISearchHit)
@component.adapter(interface.Interface, IDict)
def _default_search_hit_adapter(obj, result, hit=None):
	hit = SearchHit() if hit is None else hit
	hit.Target = obj
	hit.Score = result['score']
	hit.ID = IIDValue(obj).value()
	for value_interface, name in HIT_FIELDS:
		adapted = value_interface(obj, None)
		if adapted is not None:
			value = adapted.value()
			setattr(hit, name, value)
	return hit
