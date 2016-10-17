#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
from nti.contentfragments.interfaces import IPlainTextContentFragment
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from nti.contentlibrary.interfaces import IContentUnit
from nti.contentlibrary.interfaces import IContentPackage

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.solr.interfaces import ITitleValue
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import IKeywordsValue
from nti.solr.interfaces import IContentPackageValue
from nti.solr.interfaces import IContentUnitDocument

from nti.solr.metadata import MetadataDocument

from nti.solr.utils import get_keywords
from nti.solr.utils import document_creator

from nti.traversal.traversal import find_interface

class _BasicAttributeValue(object):

	def __init__(self, context=None):
		self.context = context

@component.adapter(IContentUnit)
@interface.implementer(IContentPackageValue)
class _DefaultContentPackageValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		package = find_interface(context, IContentPackage, strict=False)
		try:
			return package.ntiid
		except AttributeError:
			return None

@component.adapter(IContentUnit)
@interface.implementer(ITitleValue)
class _DefaultTitleValue(_BasicAttributeValue):

	def lang(self, context=None):
		return 'en'

	def value(self, context=None):
		context = self.context if context is None else context
		return context.title

@component.adapter(IContentUnit)
@interface.implementer(IContentValue)
class _DefaultContentUnitContentValue(_BasicAttributeValue):

	language = 'en'

	def get_content(self, context):
		return context.read_contents()

	def lang(self, context=None):
		return self.language

	def value(self, context=None):
		context = self.context if context is None else context
		return self.get_content(context)

@component.adapter(IContentUnit)
@interface.implementer(IKeywordsValue)
class _DefaultContentUnitKeywordsValue(_BasicAttributeValue):

	language = 'en'
	
	def lang(self, context=None):
		return self.language

	def value(self, context=None):
		context = self.context if context is None else context
		adapted = IContentValue(context, None)
		if adapted is not None:
			self.language = adapted.lang()
			content = component.getAdapter(adapted.value(), 
										   IPlainTextContentFragment, 
										   name='text')
			return get_keywords(content, self.language)
		return ()

@interface.implementer(IContentUnitDocument)
class ContentUnitDocument(MetadataDocument):
	createDirectFieldProperties(IContentUnitDocument)

	mimeType = mime_type = u'application/vnd.nextthought.solr.contentunitdocument'
		
@component.adapter(IContentUnit)
@interface.implementer(IContentUnitDocument)
def _ContentUnitDocumentCreator(obj, factory=ContentUnitDocument):
	return document_creator(obj, factory=factory)
