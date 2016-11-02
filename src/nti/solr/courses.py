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

from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseKeywords
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.solr import NTI_CATALOG
from nti.solr import COURSES_CATALOG

from nti.solr.catalog import CoreCatalog

from nti.solr.interfaces import INTIIDValue
from nti.solr.interfaces import ITitleValue
from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import IKeywordsValue
from nti.solr.interfaces import ICourseCatalogDocument

from nti.solr.metadata import MetadataDocument

from nti.solr.utils import CATALOG_MIME_TYPE_MAP

from nti.solr.utils import lucene_escape
from nti.solr.utils import document_creator

class _BasicAttributeValue(object):

	def __init__(self, context=None):
		self.context = context

	def entry(self, context):
		return ICourseCatalogEntry(context, None)

@component.adapter(ICourseInstance)
@interface.implementer(INTIIDValue)
class _DefaultNTIIDValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		return to_unicode(getattr(self.entry(context), 'ntiid', None))

@interface.implementer(ITitleValue)
@component.adapter(ICourseInstance)
class _DefaultCourseCatalogTitleValue(_BasicAttributeValue):

	def lang(self, context):
		return 'en'

	def value(self, context=None):
		context = self.context if context is None else context
		return to_unicode(getattr(self.entry(context), 'title', None))

@component.adapter(ICourseInstance)
@interface.implementer(IContentValue)
class _DefaultCourseCatalogContentValue(_BasicAttributeValue):

	language = 'en'

	def lang(self, context=None):
		return self.language

	def get_content(self, context):
		return to_unicode(getattr(context, 'description', None))

	def value(self, context=None):
		context = self.context if context is None else context
		return self.get_content(self.entry(context))

@component.adapter(ICourseInstance)
@interface.implementer(IKeywordsValue)
class _DefaultCourseCatalogKeywordsValue(_BasicAttributeValue):

	language = 'en'

	def lang(self, context=None):
		return self.language

	def value(self, context=None):
		result = ()
		context = self.context if context is None else context
		context = ICourseInstance(context, None)
		keywords = ICourseKeywords(context, None)
		if keywords:
			result = keywords.keywords or ()
		return result

@interface.implementer(ICourseCatalogDocument)
class CourseCatalogDocument(MetadataDocument):
	createDirectFieldProperties(ICourseCatalogDocument)

	mimeType = mime_type = u'application/vnd.nextthought.solr.coursecatalogdocument'

@component.adapter(ICourseInstance)
@interface.implementer(ICourseCatalogDocument)
def _CourseCatalogDocumentCreator(obj, factory=CourseCatalogDocument):
	return document_creator(obj, factory=factory, provided=ICourseCatalogDocument)

@component.adapter(ICourseInstance)
@interface.implementer(ICoreCatalog)
def _course_to_catalog(obj):
	return component.getUtility(ICoreCatalog, name=COURSES_CATALOG)

class CoursesCatalog(CoreCatalog):

	name = COURSES_CATALOG
	document_interface = ICourseCatalogDocument

	def __init__(self, core=NTI_CATALOG, client=None):
		CoreCatalog.__init__(self, core=core, client=client)

	def _build_from_search_query(self, query):
		term, fq, params = CoreCatalog._build_from_search_query(self, query)
		if 'mimeType' not in fq:
			types = CATALOG_MIME_TYPE_MAP.get(COURSES_CATALOG)
			fq['mimeType'] = "(%s)" % self._OR_.join(lucene_escape(x) for x in types)
		return term, fq, params
	
	def clear(self, commit=None):
		types = CATALOG_MIME_TYPE_MAP.get(COURSES_CATALOG)
		q = "mimeType:(%s)" % self._OR_.join(lucene_escape(x) for x in types)
		self.client.delete(q=q, commit=self.auto_commit if commit is None else bool(commit))
	reset = clear
