#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from nti.base._compat import text_

from nti.contentfragments.html import sanitize_user_html

from nti.contentfragments.interfaces import IPlainTextContentFragment

from nti.contentlibrary.interfaces import INoAutoIndex
from nti.contentlibrary.interfaces import IContentUnit
from nti.contentlibrary.interfaces import IContentPackage
from nti.contentlibrary.interfaces import IRenderableContentUnit

from nti.coremetadata.interfaces import SYSTEM_USER_NAME

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.solr import CONTENT_UNITS_CATALOG

from nti.solr.interfaces import ITitleValue
from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import ICreatorValue
from nti.solr.interfaces import IKeywordsValue
from nti.solr.interfaces import IContainersValue
from nti.solr.interfaces import ICreatedTimeValue
from nti.solr.interfaces import IContentUnitDocument

from nti.solr.lucene import lucene_escape

from nti.solr.metadata import ZERO_DATETIME
from nti.solr.metadata import MetadataCatalog
from nti.solr.metadata import MetadataDocument
from nti.solr.metadata import DefaultObjectIDValue

from nti.solr.utils import get_keywords
from nti.solr.utils import document_creator

from nti.traversal.location import lineage


class _BasicAttributeValue(object):

    def __init__(self, context=None, _=None):
        self.context = context


@component.adapter(IContentUnit)
class _DefaultContentUnitIDValue(DefaultObjectIDValue):

    @classmethod
    def createdTime(cls, _):
        return ZERO_DATETIME

    @classmethod
    def creator(cls, _):
        return SYSTEM_USER_NAME

    def value(self, context=None):
        context = self.context if context is None else context
        if not INoAutoIndex.providedBy(context):
            return self.prefix(context) + context.ntiid
        return None


@component.adapter(IRenderableContentUnit)
class _RenderableContentUnitIDValue(_DefaultContentUnitIDValue):

    @classmethod
    def createdTime(cls, context):
        adapted = ICreatedTimeValue(context, None)
        value = adapted.value() if adapted is not None else None
        return value or ZERO_DATETIME

    @classmethod
    def creator(cls, context):
        adapted = ICreatorValue(context, None)
        value = adapted.value() if adapted is not None else None
        return value or SYSTEM_USER_NAME


@component.adapter(IContentUnit)
@interface.implementer(IContainersValue)
class _DefaultContainerIdValue(_BasicAttributeValue):

    def value(self, context=None):
        result = list()
        context = self.context if context is None else context
        for item in lineage(context):
            if IContentUnit.providedBy(item) and item.ntiid:
                result.append(item.ntiid)
            if IContentPackage.providedBy(item):
                break
        return tuple(result)


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
        parent_key = getattr(context.__parent__, 'key', None)
        if     parent_key is None \
            or parent_key.absolute_path != context.key.absolute_path:  # don't index twice
            return sanitize_user_html(text_(context.read_contents()))
        return None

    def lang(self, context=None):
        return self.language

    def value(self, context=None):
        context = self.context if context is None else context
        return self.get_content(context)


@component.adapter(IRenderableContentUnit)
class _RenderableContentUnitContentValue(_DefaultContentUnitContentValue):

    def get_content(self, context):
        value = super(_RenderableContentUnitContentValue, self).get_content(context)
        if value is not None:
            value = IPlainTextContentFragment(value)
        return value


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

    mimeType = mime_type = 'application/vnd.nextthought.solr.contentunitdocument'


@component.adapter(IContentUnit)
@interface.implementer(IContentUnitDocument)
def _ContentUnitDocumentCreator(obj, factory=ContentUnitDocument):
    return document_creator(obj, factory=factory)


@component.adapter(IContentUnit)
@interface.implementer(ICoreCatalog)
def _contentunit_to_catalog(_):
    return component.getUtility(ICoreCatalog, name=CONTENT_UNITS_CATALOG)


class ContentUnitsCatalog(MetadataCatalog):

    name = CONTENT_UNITS_CATALOG
    document_interface = IContentUnitDocument

    return_fields = ('id', 'score', 'containerId')

    def build_from_search_query(self, query, **kwargs):
        term, fq, params = MetadataCatalog.build_from_search_query(self, query, **kwargs)
        if 'mimeType' not in fq:
            types = self.get_mime_types(self.name)
            fq.add_or('mimeType', [lucene_escape(x) for x in types])
        return term, fq, params

    def clear(self, commit=None, mimeTypes=()):
        types = mimeTypes or self.get_mime_types(self.name)
        q = "mimeType:(%s)" % self._OR_.join(lucene_escape(x) for x in types)
        commit = self.auto_commit if commit is None else bool(commit)
        self.client.delete(q=q, commit=commit)
    reset = clear


# jobs


from zope.component.hooks import site as current_site

from nti.contenttypes.presentation.interfaces import IPresentationAssetContainer

from nti.solr.common import finder
from nti.solr.common import get_job_site
from nti.solr.common import process_asset


def process_content_package(obj, index=True):
    def recur(unit):
        for child in unit.children or ():
            recur(child)
        catalog = ICoreCatalog(unit)
        operation = catalog.add if index else catalog.remove
        operation(unit, commit=False)  # wait for server to commit
    recur(obj)


def index_content_package(source, site=None, *args, **kwargs):
    job_site = get_job_site(site)
    with current_site(job_site):
        obj = finder(source)
        if IContentPackage.providedBy(obj):
            logger.info("Content package indexing %s started", obj.ntiid)
            process_content_package(obj, index=True)
            logger.info("Content package indexing %s completed", obj.ntiid)


def unindex_content_package(source, site=None, **kwargs):
    job_site = get_job_site(site)
    with current_site(job_site):
        obj = finder(source)
        if IContentPackage.providedBy(obj):
            process_content_package(obj, index=False)


def process_content_package_assets(obj, index=True):
    collector = set()

    def recur(unit):
        container = IPresentationAssetContainer(unit, None)
        if container:
            collector.update(container.values())
        for child in unit.children or ():
            recur(child)
    recur(obj)
    for obj in collector:
        # wait for server to commit
        process_asset(obj, index=index, commit=False)


def index_content_package_assets(source, site=None, *args, **kwargs):
    job_site = get_job_site(site)
    with current_site(job_site):
        obj = finder(source)
        if IContentPackage.providedBy(obj):
            logger.info("Content package %s assets indexing started",
                        obj.ntiid)
            process_content_package_assets(obj, index=True)
            logger.info("Content package %s assets indexing completed",
                        obj.ntiid)


def unindex_content_package_assets(source, site=None, *args, **kwargs):
    job_site = get_job_site(site)
    with current_site(job_site):
        obj = finder(source)
        if IContentPackage.providedBy(obj):
            process_content_package_assets(obj, index=False)
