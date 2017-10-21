#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component
from zope import interface

from nti.base._compat import text_

from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseKeywords
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.solr import COURSES_CATALOG

from nti.solr.interfaces import ITagsValue
from nti.solr.interfaces import INTIIDValue
from nti.solr.interfaces import ITitleValue
from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import IKeywordsValue
from nti.solr.interfaces import ICourseCatalogDocument

from nti.solr.lucene import lucene_escape

from nti.solr.metadata import MetadataCatalog
from nti.solr.metadata import MetadataDocument

from nti.solr.utils import document_creator

logger = __import__('logging').getLogger(__name__)


class _BasicAttributeValue(object):

    def __init__(self, context=None, unused_default=None):
        self.context = context

    def entry(self, context):
        return ICourseCatalogEntry(context, None)


@component.adapter(ICourseInstance)
@interface.implementer(INTIIDValue)
class _DefaultNTIIDValue(_BasicAttributeValue):

    def value(self, context=None):
        context = self.context if context is None else context
        return text_(getattr(self.entry(context), 'ntiid', None))


@interface.implementer(ITitleValue)
@component.adapter(ICourseInstance)
class _DefaultCourseCatalogTitleValue(_BasicAttributeValue):

    def lang(self, unused_context=None):
        return 'en'

    def value(self, context=None):
        context = self.context if context is None else context
        return text_(getattr(self.entry(context), 'title', None))


@component.adapter(ICourseInstance)
@interface.implementer(IContentValue)
class _DefaultCourseCatalogContentValue(_BasicAttributeValue):

    language = 'en'

    def lang(self, unused_context=None):
        return self.language

    def get_content(self, context):
        return text_(getattr(context, 'description', None))

    def value(self, context=None):
        context = self.context if context is None else context
        return self.get_content(self.entry(context))


@component.adapter(ICourseInstance)
@interface.implementer(IKeywordsValue)
class _DefaultCourseCatalogKeywordsValue(_BasicAttributeValue):

    language = 'en'

    def lang(self, unused_context=None):
        return self.language

    def value(self, context=None):
        result = ()
        context = self.context if context is None else context
        context = ICourseInstance(context, None)
        keywords = ICourseKeywords(context, None)
        if keywords:
            result = keywords.keywords or ()
            result = [text_(x) for x in result]
        return result


@interface.implementer(ITagsValue)
@component.adapter(ICourseInstance)
class _DefaultCourseCatalogTagsValue(_BasicAttributeValue):

    def value(self, context=None):
        context = self.context if context is None else context
        entry = ICourseCatalogEntry(context, None)
        return getattr(entry, 'tags', None) or ()


@interface.implementer(ICourseCatalogDocument)
class CourseCatalogDocument(MetadataDocument):
    createDirectFieldProperties(ICourseCatalogDocument)

    mimeType = mime_type = 'application/vnd.nextthought.solr.coursecatalogdocument'


@component.adapter(ICourseInstance)
@interface.implementer(ICourseCatalogDocument)
def _CourseCatalogDocumentCreator(obj, factory=CourseCatalogDocument):
    return document_creator(obj, factory=factory, provided=ICourseCatalogDocument)


@component.adapter(ICourseInstance)
@interface.implementer(ICoreCatalog)
def _course_to_catalog(unused_context):
    return component.getUtility(ICoreCatalog, name=COURSES_CATALOG)


class CoursesCatalog(MetadataCatalog):

    name = COURSES_CATALOG
    document_interface = ICourseCatalogDocument

    def build_from_search_query(self, query, **kwargs):
        term, fq, params = MetadataCatalog.build_from_search_query(self, query, **kwargs)
        if 'mimeType' not in fq:
            types = self.get_mime_types(self.name)
            fq.add_or('mimeType', [lucene_escape(x) for x in types])
        return term, fq, params

    def clear(self, commit=None):
        types = self.get_mime_types(self.name)
        q = "mimeType:(%s)" % self._OR_.join(lucene_escape(x) for x in types)
        commit=self.auto_commit if commit is None else bool(commit)
        self.client.delete(q=q, commit=commit)
    reset = clear
