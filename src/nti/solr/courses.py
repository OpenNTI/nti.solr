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

from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseKeywords
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.solr.interfaces import ITitleValue
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import IKeywordsValue
from nti.solr.interfaces import ICourseCatalogDocument

from nti.solr.metadata import MetadataDocument

from nti.solr.utils import document_creator

class _BasicAttributeValue(object):

	def __init__(self, context=None):
		self.context = context

@interface.implementer(ITitleValue)
@component.adapter(ICourseCatalogEntry)
class _DefaultCourseCatalogTitleValue(_BasicAttributeValue):

	def lang(self, context):
		return 'en'

	def value(self, context=None):
		context = self.context if context is None else context
		return getattr(context, 'title', None)

@interface.implementer(IContentValue)
@component.adapter(ICourseCatalogEntry)
class _DefaultCourseCatalogContentValue(_BasicAttributeValue):

	language = 'en'

	def lang(self, context=None):
		return self.language

	def get_content(self, context):
		return getattr( context, 'description', None )

	def value(self, context=None):
		context = self.context if context is None else context
		return self.get_content(context)

@component.adapter(ICourseCatalogEntry)
@interface.implementer(IKeywordsValue)
class _DefaultCourseCatalogKeywordsValue(_BasicAttributeValue):

	language = 'en'

	def lang(self, context=None):
		return self.language

	def value(self, context=None):
		context = self.context if context is None else context
		context = ICourseInstance( context, None )
		keywords = ICourseKeywords( context, None )
		result = ()
		if keywords:
			result = keywords.keywords or ()
		return result

@interface.implementer(ICourseCatalogDocument)
class CourseCatalogDocument(MetadataDocument):
	createDirectFieldProperties(ICourseCatalogDocument)

	mimeType = mime_type = u'application/vnd.nextthought.solr.coursecatalogdocument'

@component.adapter(ICourseCatalogEntry)
@interface.implementer(ICourseCatalogDocument)
def _CourseCatalogDocumentCreator(obj, factory=CourseCatalogDocument):
	return document_creator(obj, factory=factory, provided=ICourseCatalogDocument)
