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

from nti.contentlibrary.interfaces import IContentUnit, IContentPackage

from nti.contenttypes.presentation.interfaces import IUserCreatedAsset
from nti.contenttypes.presentation.interfaces import IPresentationAsset

from nti.coremetadata.interfaces import SYSTEM_USER_NAME

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.solr import NTI_CATALOG
from nti.solr import ASSETS_CATALOG

from nti.solr.catalog import CoreCatalog

from nti.solr.interfaces import ITitleValue
from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import ICreatorValue
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import IKeywordsValue
from nti.solr.interfaces import IAssetDocument
from nti.solr.interfaces import IContainerIdValue

from nti.solr.metadata import ZERO_DATETIME
from nti.solr.metadata import MetadataDocument
from nti.solr.metadata import DefaultObjectIDValue

from nti.solr.utils import get_keywords
from nti.solr.utils import document_creator

from nti.traversal.location import lineage

class _BasicAttributeValue(object):

	def __init__(self, context=None):
		self.context = context

@component.adapter(IContentUnit)
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
		if IUserCreatedAsset.providedBy(context):
			return super(_DefaultAssetIDValue, self).creator(context)
		return self.prefix(context) + context.ntiid

@interface.implementer(ITitleValue)
@component.adapter(IPresentationAsset)
class _DefaultAssetTitleValue(_BasicAttributeValue):

	def lang(self, context):
		return 'en'

	def value(self, context=None):
		context = self.context if context is None else context
		return 		getattr(context, 'title', None) \
				or	getattr(context, 'label', None)

@interface.implementer(ICreatorValue)
@component.adapter(IPresentationAsset)
class _DefaultAssetCreatorValue(_BasicAttributeValue):

	def lang(self, context):
		return 'en'

	def value(self, context=None):
		context = self.context if context is None else context
		result = 	getattr(context, 'byline', None) \
			  	or	getattr(context, 'creator', None)
		result = getattr(result, 'username', result)
		return result.lower() if result else None

@component.adapter(IPresentationAsset)
@interface.implementer(IContainerIdValue)
class _DefaultContainerIdValue(_BasicAttributeValue):

	def _containers(self, context, break_interface):
		result = set()
		for item in lineage(context):
			try:
				ntiid = item.ntiid
				if ntiid:
					result.add(ntiid)
			except AttributeError:
				pass
			if break_interface.providedBy(item):
				return result,item
		return result, None

	def value(self, context=None):
		context = self.context if context is None else context
		containers, _ = self._containers(context, IContentPackage)
		if not containers:
			try:
				from nti.contenttypes.courses.interfaces import ICourseInstance
				from nti.contenttypes.courses.interfaces import ICourseCatalogEntry
				containers, item = self._containers(context, ICourseInstance)
				containers.add(getattr(ICourseCatalogEntry(item, None), 'ntiid', None))
				containers.discard(None)
			except ImportError:
				pass
		return tuple(containers)

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

@interface.implementer(IAssetDocument)
class AssetDocument(MetadataDocument):
	createDirectFieldProperties(IAssetDocument)

	mimeType = mime_type = u'application/vnd.nextthought.solr.assetdocument'

@component.adapter(IPresentationAsset)
@interface.implementer(IAssetDocument)
def _AssetDocumentCreator(obj, factory=AssetDocument):
	return document_creator(obj, factory=factory, provided=IAssetDocument)

@component.adapter(IContentUnit)
@interface.implementer(ICoreCatalog)
def _asset_to_catalog(obj):
	return component.getUtility(ICoreCatalog, name=ASSETS_CATALOG)

class AssetsCatalog(CoreCatalog):

	document_interface = IAssetDocument

	def __init__(self, name=NTI_CATALOG, client=None):
		CoreCatalog.__init__(self, name=name, client=client)
