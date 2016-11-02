#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six

from zope import component
from zope import interface

from nti.common.string import to_unicode

from nti.contentindexing.media.interfaces import IAudioTranscriptParser
from nti.contentindexing.media.interfaces import IVideoTranscriptParser

from nti.contentlibrary.interfaces import IContentPackage

from nti.contenttypes.presentation.interfaces import INTIVideo
from nti.contenttypes.presentation.interfaces import INTITranscript

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.solr import NTI_CATALOG
from nti.solr import TRANSCRIPTS_CATALOG

from nti.solr.catalog import CoreCatalog

from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import IKeywordsValue
from nti.solr.interfaces import IMediaNTIIDValue
from nti.solr.interfaces import ITranscriptDocument

from nti.solr.metadata import MetadataDocument

from nti.solr.utils import CATALOG_MIME_TYPE_MAP

from nti.solr.utils import get_keywords
from nti.solr.utils import lucene_escape
from nti.solr.utils import document_creator
from nti.solr.utils import get_item_content_package

from nti.traversal.traversal import find_interface

class _BasicAttributeValue(object):

	def __init__(self, context=None):
		self.context = context

@component.adapter(INTITranscript)
@interface.implementer(IIDValue)
class _TranscriptIDValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		return context.ntiid

@component.adapter(INTITranscript)
@interface.implementer(IMediaNTIIDValue)
class _TranscriptMediaNTIIDValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		try:
			parent = context.__parent__
			return parent.ntiid
		except AttributeError:
			return None

@component.adapter(INTITranscript)
@interface.implementer(IContentValue)
class _TranscriptContentValue(_BasicAttributeValue):

	@classmethod
	def parse_content(cls, context, raw_content):
		type_ = context.type or "text/vtt"
		if INTIVideo.providedBy(context.__parent__):
			provided = IVideoTranscriptParser
		else:
			provided = IAudioTranscriptParser
		parser = component.queryUtility(provided, name=type_)
		if parser is not None:
			transcript = parser.parse(to_unicode(raw_content))
			return to_unicode(transcript.text)
		return None

	@classmethod
	def get_content(cls, context):
		src = context.src
		raw_content = None
		# is in content pkg ?
		if 		isinstance(src, six.string_types) \
			and not src.startswith('/')  \
			and '://' not in src:  # e.g. resources/...
			package = find_interface(context, IContentPackage, strict=False)
			if package is None:
				package = get_item_content_package(context)
			try:
				raw_content = package.read_contents_of_sibling_entry(src)
			except Exception:
				logger.exception("Cannot read contents for %s", src)
		if raw_content:
			return cls.parse_content(context, raw_content)
		return None

	def lang(self, context=None):
		context = self.context if context is None else context
		return context.lang

	def value(self, context=None):
		context = self.context if context is None else context
		return self.get_content(context)

@component.adapter(INTITranscript)
@interface.implementer(IKeywordsValue)
class _TranscriptKeywordsValue(_BasicAttributeValue):

	def lang(self, context=None):
		context = self.context if context is None else context
		return context.lang

	def value(self, context=None):
		context = self.context if context is None else context
		adapted = IContentValue(context, None)
		if adapted is not None:
			return get_keywords(adapted.value(), self.lang(context))
		return ()

@interface.implementer(ITranscriptDocument)
class TranscriptDocument(MetadataDocument):
	createDirectFieldProperties(ITranscriptDocument)

	mimeType = mime_type = u'application/vnd.nextthought.solr.transcriptdocument'

@component.adapter(INTITranscript)
@interface.implementer(ITranscriptDocument)
def _TranscriptDocumentCreator(obj, factory=TranscriptDocument):
	return document_creator(obj, factory=factory, provided=ITranscriptDocument)

@component.adapter(INTITranscript)
@interface.implementer(ICoreCatalog)
def _transcript_to_catalog(obj):
	return component.getUtility(ICoreCatalog, name=TRANSCRIPTS_CATALOG)

class TranscriptsCatalog(CoreCatalog):

	document_interface = ITranscriptDocument

	def __init__(self, name=NTI_CATALOG, client=None):
		CoreCatalog.__init__(self, name=name, client=client)

	def _build_from_search_query(self, query):
		term, fq, params = CoreCatalog._build_from_search_query(self, query)
		if 'mimeType' not in fq:
			types = CATALOG_MIME_TYPE_MAP.get(TRANSCRIPTS_CATALOG)
			fq['mimeType'] = "(%s)" % self._OR_.join(lucene_escape(x) for x in types)
		return term, fq, params

	def clear(self, commit=None):
		types = CATALOG_MIME_TYPE_MAP.get(TRANSCRIPTS_CATALOG)
		q = "mimeType:(%s)" % self._OR_.join(lucene_escape(x) for x in types)
		self.client.delete(q=q, commit=self.auto_commit if commit is None else bool(commit))
	reset = clear
