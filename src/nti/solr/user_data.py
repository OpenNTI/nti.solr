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

from nti.dataserver.interfaces import IUserGeneratedData

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.solr.interfaces import ITitleValue
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import IKeywordsValue
from nti.solr.interfaces import IUserDataDocument

from nti.solr.metadata import MetadataDocument

from nti.solr.utils import get_keywords
from nti.solr.utils import document_creator

class _BasicAttributeValue(object):

	def __init__(self, context=None):
		self.context = context

@interface.implementer(ITitleValue)
@component.adapter(IUserGeneratedData)
class _DefaultUserDataTitleValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		return getattr(context, 'title', None)

@interface.implementer(IContentValue)
@component.adapter(IUserGeneratedData)
class _DefaultUserDataContentValue(_BasicAttributeValue):

	@classmethod
	def get_content(cls, context):
		return None

	def value(self, context=None):
		context = self.context if context is None else context
		return self.get_content(context)

@component.adapter(IUserGeneratedData)
@interface.implementer(IKeywordsValue)
class _DefaultUserDataKeywordsValue(_DefaultUserDataContentValue):

	def value(self, context=None):
		context = self.context if context is None else context
		text = super(_DefaultUserDataKeywordsValue, self).value(context)
		return get_keywords(text, context.lang)

@interface.implementer(IUserDataDocument)
class UserDataDocument(MetadataDocument):
	createDirectFieldProperties(IUserDataDocument)

	mimeType = mime_type = u'application/vnd.nextthought.solr.usergenerateddatadocument'
		
@component.adapter(IUserGeneratedData)
@interface.implementer(IUserDataDocument)
def _UserDataDocumentCreator(obj, factory=UserDataDocument):
	return document_creator(obj, factory=factory)
