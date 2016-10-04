#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six
import pytz
from datetime import datetime

from zope import component
from zope import interface

from zope.intid.interfaces import IIntIds

from zope.mimetype.interfaces import IContentTypeAware

from nti.coremetadata.interfaces import ICreatedTime
from nti.coremetadata.interfaces import ILastModified

from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import ICreatorValue
from nti.solr.interfaces import IMimeTypeValue
from nti.solr.interfaces import ICreatedTimeValue
from nti.solr.interfaces import ILastModifiedValue

class _BasicAttributeValue(object):

	def __init__(self, context):
		self.context = context

@interface.implementer(ICreatorValue)
class _DefaultCreatorValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		try:
			creator = context.creator
			creator = getattr(creator, 'username', creator)
			if isinstance(creator, six.string_types):
				return creator.lower()
		except (AttributeError, TypeError):
			pass
		return None

@interface.implementer(IIDValue)
class _DefaultIDValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		try:
			initds = component.getUtility(IIntIds)
			result = initds.queryId(context)
			return unicode(result) if result is not None else None
		except (LookupError, KeyError):
			pass
		return None

@interface.implementer(IMimeTypeValue)
class _DefaultMimeTypeValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		context = IContentTypeAware(context, context)
		return getattr(context, 'mimeType', None) or getattr(context, 'mime_type', None)

@interface.implementer(ICreatedTimeValue)
class _DefaultCreatedTimeValue(_BasicAttributeValue):

	attribute = 'createdTime'
	interface = ICreatedTime
	
	def value(self, context=None):
		context = self.context if context is None else context
		context = self.interface(context, context)
		if context is not None:
			result = getattr(context, self.attribute, None) or 0
			result = datetime.fromtimestamp(result, pytz.utc)
			return result.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
		return None

@interface.implementer(ILastModifiedValue)
class _DefaultLastModifiedValue(_DefaultCreatedTimeValue):
	attribute = 'lastModified'
	interface = ILastModified
