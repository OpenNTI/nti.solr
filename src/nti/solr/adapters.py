#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from nti.common.string import to_unicode

from nti.dataserver.interfaces import IUserGeneratedData

from nti.solr.interfaces import ICoreCatalog 
from nti.solr.interfaces import IStringValue 

from nti.solr.catalog import CoreCatalog

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

@interface.implementer(ICoreCatalog)
@component.adapter(IUserGeneratedData)
def _UserDataCatalog(obj):
	return CoreCatalog('user_data')
