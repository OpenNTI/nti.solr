#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from six import string_types

from zope import component
from zope import interface

from nti.contenttypes.presentation import RELATED_WORK

from nti.contenttypes.presentation.interfaces import IPointer
from nti.contenttypes.presentation.interfaces import IUserCreatedAsset
from nti.contenttypes.presentation.interfaces import IPresentationAsset

from nti.coremetadata.interfaces import SYSTEM_USER_NAME

from nti.ntiids.ntiids import is_ntiid_of_type

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.solr import ASSETS_CATALOG

from nti.solr.interfaces import ITitleValue
from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import ITargetValue
from nti.solr.interfaces import ICreatorValue
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import IKeywordsValue
from nti.solr.interfaces import IAssetDocument

from nti.solr.lucene import lucene_escape

from nti.solr.metadata import ZERO_DATETIME
from nti.solr.metadata import MetadataCatalog
from nti.solr.metadata import MetadataDocument
from nti.solr.metadata import DefaultObjectIDValue

from nti.solr.utils import get_keywords
from nti.solr.utils import document_creator


class _BasicAttributeValue(object):

    def __init__(self, context=None, default=None):
        self.context = context


@component.adapter(IPresentationAsset)
class _DefaultAssetIDValue(DefaultObjectIDValue):

    @classmethod
    def createdTime(cls, context):
        if IUserCreatedAsset.providedBy(context):
            return super(_DefaultAssetIDValue, cls).createdTime(context)
        return ZERO_DATETIME

    @classmethod
    def creator(cls, context):
        if IUserCreatedAsset.providedBy(context):
            return super(_DefaultAssetIDValue, cls).creator(context)
        return SYSTEM_USER_NAME

    def value(self, context=None):
        context = self.context if context is None else context
        # Filter out legacy RelatedWork ntiids.
        if is_ntiid_of_type(context.ntiid, RELATED_WORK):
            result = None
        elif IUserCreatedAsset.providedBy(context):
            result = super(_DefaultAssetIDValue, self).creator(context)
        else:
            result = self.prefix(context) + context.ntiid
        return result


@interface.implementer(ITitleValue)
@component.adapter(IPresentationAsset)
class _DefaultAssetTitleValue(_BasicAttributeValue):

    def lang(self, context):
        return 'en'

    def value(self, context=None):
        context = self.context if context is None else context
        return 		getattr(context, 'title', None) \
            or getattr(context, 'label', None)


@interface.implementer(ICreatorValue)
@component.adapter(IPresentationAsset)
class _DefaultAssetCreatorValue(_BasicAttributeValue):

    def lang(self, context):
        return 'en'

    def value(self, context=None):
        context = self.context if context is None else context
        result =  getattr(context, 'byline', None) \
            or getattr(context, 'creator', None)
        result = getattr(result, 'username', result)
        return result.lower() if result else None


@interface.implementer(IContentValue)
@component.adapter(IPresentationAsset)
class _DefaultAssetContentValue(_BasicAttributeValue):

    language = 'en'

    def lang(self, context=None):
        return self.language

    def get_content(self, context):
        return getattr(context, 'description', None)

    def value(self, context=None):
        context = self.context if context is None else context
        return self.get_content(context)


@component.adapter(IPresentationAsset)
@interface.implementer(IKeywordsValue)
class _DefaultAssetKeywordsValue(_BasicAttributeValue):

    language = 'en'

    def lang(self, context=None):
        return self.language

    def value(self, context=None):
        context = self.context if context is None else context
        adapted = IContentValue(context, None)
        if adapted is not None:
            self.language = adapted.lang()
            return get_keywords(adapted.value(), self.language)
        return ()


@interface.implementer(ITargetValue)
@component.adapter(IPresentationAsset)
class _DefaultTargetValue(_BasicAttributeValue):

    def value(self, context=None):
        context = self.context if context is None else context
        if IPointer.providedBy(context):
            return context.target
        return None


@interface.implementer(IAssetDocument)
class AssetDocument(MetadataDocument):
    createDirectFieldProperties(IAssetDocument)

    mimeType = mime_type = u'application/vnd.nextthought.solr.assetdocument'


@component.adapter(IPresentationAsset)
@interface.implementer(IAssetDocument)
def _AssetDocumentCreator(obj, factory=AssetDocument):
    return document_creator(obj, factory=factory, provided=IAssetDocument)


@interface.implementer(ICoreCatalog)
@component.adapter(IPresentationAsset)
def _asset_to_catalog(obj):
    return component.getUtility(ICoreCatalog, name=ASSETS_CATALOG)


class AssetsCatalog(MetadataCatalog):

    name = ASSETS_CATALOG
    document_interface = IAssetDocument

    def build_from_search_query(self, query):
        term, fq, params = MetadataCatalog.build_from_search_query(self, query)
        packs = getattr(query, 'packages', None) \
            or getattr(query, 'package', None)
        if 'containerId' not in fq and packs:
            packs = packs.split() if isinstance(packs, string_types) else packs
            fq.add_or('containerId', [lucene_escape(x) for x in packs])
        if 'mimeType' not in fq:
            types = self.get_mime_types(self.name)
            fq.add_or('mimeType', [lucene_escape(x) for x in types])
        return term, fq, params

    def clear(self, commit=None):
        types = self.get_mime_types(self.name)
        q = "mimeType:(%s)" % self._OR_.join(lucene_escape(x) for x in types)
        self.client.delete(
            q=q, commit=self.auto_commit if commit is None else bool(commit))
    reset = clear
