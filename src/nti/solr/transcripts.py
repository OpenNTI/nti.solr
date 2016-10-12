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

from nti.contentindexing.media.interfaces import IAudioTranscriptParser
from nti.contentindexing.media.interfaces import IVideoTranscriptParser

from nti.contentlibrary.interfaces import IContentPackage

from nti.contenttypes.presentation.interfaces import INTIVideo
from nti.contenttypes.presentation.interfaces import INTITranscript

from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import IKeywordsValue

from nti.solr.utils import get_keywords
from nti.solr.utils import get_item_content_package

from nti.traversal.traversal import find_interface

@component.adapter(INTITranscript)
@interface.implementer(IIDValue)
class _TranscriptIDValue(object):

	def __init__(self, context):
		self.context = context

	def value(self, context=None):
		context = self.context if context is None else context
		return context.ntiid

@component.adapter(INTITranscript)
@interface.implementer(IContentValue)
class _TranscriptContentValue(object):

	def __init__(self, context):
		self.context = context

	@classmethod
	def parse_content(cls, context, raw_content):
		type_ = context.type or "text/vtt"
		if INTIVideo.providedBy(context.__parent_):
			provided = IVideoTranscriptParser
		else:
			provided = IAudioTranscriptParser
		parser = component.queryUtility(provided, name=type_)
		if parser is not None:
			transcript = parser.parse(raw_content)
			return transcript.text
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

	def value(self, context=None):
		context = self.context if context is None else context
		return self.get_content(context)

@component.adapter(INTITranscript)
@interface.implementer(IKeywordsValue)
class _TranscriptKeywordsValue(_TranscriptContentValue):

	def value(self, context=None):
		context = self.context if context is None else context
		text = super(_TranscriptKeywordsValue, self).value(context)
		return get_keywords(text, context.lang)
