#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import six

from zope import component
from zope import interface

from zope.event import notify

from nti.base._compat import text_

from nti.contentindexing.media.interfaces import IMediaTranscriptEntry
from nti.contentindexing.media.interfaces import IAudioTranscriptParser
from nti.contentindexing.media.interfaces import IVideoTranscriptParser

from nti.contentindexing.utils import media_date_to_millis
from nti.contentindexing.utils import mediatimestamp_to_datetime

from nti.contenttypes.presentation.interfaces import INTIVideo
from nti.contenttypes.presentation.interfaces import INTITranscript
from nti.contenttypes.presentation.interfaces import IUserCreatedAsset

from nti.coremetadata.interfaces import SYSTEM_USER_NAME

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import IIntIdValue
from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import IMimeTypeValue
from nti.solr.interfaces import IMetadataDocument
from nti.solr.interfaces import ITranscriptCatalog

from nti.solr.interfaces import ObjectIndexedEvent
from nti.solr.interfaces import ObjectUnindexedEvent

from nti.solr.lucene import lucene_escape

from nti.solr.metadata import ZERO_DATETIME
from nti.solr.metadata import MetadataCatalog
from nti.solr.metadata import MetadataDocument
from nti.solr.metadata import DefaultObjectIDValue
from nti.solr.metadata import DefaultObjectIntIdValue

from nti.solr.presentation import TRANSCRIPTS_CATALOG
from nti.solr.presentation import NTI_TRANSCRIPT_MIME_TYPE

from nti.solr.presentation.interfaces import IMediaNTIIDValue
from nti.solr.presentation.interfaces import ITranscriptDocument
from nti.solr.presentation.interfaces import ITranscriptSourceValue
from nti.solr.presentation.interfaces import ITranscriptCueEndTimeValue
from nti.solr.presentation.interfaces import ITranscriptCueStartTimeValue

from nti.solr.utils import object_finder
from nti.solr.utils import document_creator

logger = __import__('logging').getLogger(__name__)


class _BasicAttributeValue(object):

    def __init__(self, context=None, unused_default=None):
        self.context = context


@interface.implementer(IIDValue)
@component.adapter(INTITranscript)
class _TranscriptIDValue(DefaultObjectIDValue):

    @classmethod
    def createdTime(cls, context):
        if IUserCreatedAsset.providedBy(context.__parent__):
            return super(_TranscriptIDValue, cls).createdTime(context)
        return ZERO_DATETIME

    @classmethod
    def creator(cls, context):
        if IUserCreatedAsset.providedBy(context.__parent__):
            return super(_TranscriptIDValue, cls).creator(context)
        return SYSTEM_USER_NAME

    def value(self, context=None):
        context = self.context if context is None else context
        return self.prefix(context) + context.ntiid


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
@interface.implementer(IIntIdValue)
class _TranscriptIntIdValue(DefaultObjectIntIdValue):

    def value(self, context=None):
        context = self.context if context is None else context
        try:
            parent = context.__parent__
            return super(_TranscriptIntIdValue, self).value(parent)
        except AttributeError:
            return None


@component.adapter(INTITranscript)
@interface.implementer(IContentValue)
class _TranscriptContentValue(_BasicAttributeValue):

    @classmethod
    def transcript(cls, context, raw_content):
        type_ = context.type or "text/vtt"
        if INTIVideo.providedBy(context.__parent__):
            provided = IVideoTranscriptParser
        else:
            provided = IAudioTranscriptParser
        if raw_content is not None:
            parser = component.queryUtility(provided, name=type_)
            if parser is not None:
                return parser.parse(raw_content)
        return None

    @classmethod
    def parse_content(cls, context, raw_content):
        transcript = cls.transcript(context, raw_content)
        if transcript is not None:
            return text_(transcript.text)
        return None

    @classmethod
    def raw_content(cls, context):
        # pylint: disable=too-many-function-args
        source = ITranscriptSourceValue(context, None)
        return source.value() if source is not None else None

    @classmethod
    def get_content(cls, context):
        raw_content = cls.raw_content(context)
        if raw_content is not None:
            return cls.parse_content(context, raw_content)
        return None

    @classmethod
    def entries(cls, context):
        raw_content = cls.raw_content(context)
        transcript = cls.transcript(context, raw_content)
        if transcript is not None:
            return transcript.entries
        return ()

    def lang(self, context=None):
        context = self.context if context is None else context
        return context.lang

    def value(self, context=None):
        context = self.context if context is None else context
        return self.get_content(context)


TranscriptContentValue = _TranscriptContentValue


@interface.implementer(IContentValue)
@component.adapter(IMediaTranscriptEntry)
class _TranscriptCueContentValue(_BasicAttributeValue):

    language = 'en'

    def lang(self, context=None):
        context = self.context if context is None else context
        return context.language or self.language

    def value(self, context=None):
        context = self.context if context is None else context
        return context.transcript


@interface.implementer(IMimeTypeValue)
@component.adapter(IMediaTranscriptEntry)
class _TranscriptCueMimeTypeValue(_BasicAttributeValue):

    def value(self, unused_context=None):
        return NTI_TRANSCRIPT_MIME_TYPE


@component.adapter(IMediaTranscriptEntry)
@interface.implementer(ITranscriptCueStartTimeValue)
class _TranscriptCueStartTime(_BasicAttributeValue):

    def value(self, context=None):
        context = self.context if context is None else context
        if context.start_timestamp:
            result = mediatimestamp_to_datetime(context.start_timestamp)
            return media_date_to_millis(result)
        return None


@component.adapter(IMediaTranscriptEntry)
@interface.implementer(ITranscriptCueEndTimeValue)
class _TranscriptCueEndTime(_BasicAttributeValue):

    def value(self, context=None):
        context = self.context if context is None else context
        if context.end_timestamp:
            result = mediatimestamp_to_datetime(context.end_timestamp)
            return media_date_to_millis(result)
        return None


@interface.implementer(ITranscriptDocument)
class TranscriptDocument(MetadataDocument):
    createDirectFieldProperties(ITranscriptDocument)

    mimeType = mime_type = 'application/vnd.nextthought.solr.transcriptdocument'


@component.adapter(INTITranscript)
@component.adapter(IMediaTranscriptEntry)
@interface.implementer(ICoreCatalog)
def _transcript_to_catalog(unused_obj):
    return component.getUtility(ICoreCatalog, name=TRANSCRIPTS_CATALOG)


POST_FIX_SEP = u'='


def _transcript_documents_creator(transcript, factory=TranscriptDocument):
    if INTITranscript.providedBy(transcript):
        result = []
        # pylint: disable=too-many-function-args
        uid = IIDValue(transcript).value()
        media = IMediaNTIIDValue(transcript).value()
        source = document_creator(transcript,
                                  factory=MetadataDocument,
                                  provided=IMetadataDocument)
        for x, entry in enumerate(TranscriptContentValue.entries(transcript)):
            # pylint: disable=attribute-defined-outside-init
            doc = factory()
            doc.__dict__.update(source.__dict__)  # update with source
            doc.id = u"%s%s%s" % (uid, POST_FIX_SEP, x)  # = is id postfix
            doc.media = media  # ntiid of the media object
            doc.content_en = IContentValue(entry).value()
            doc.cue_end_time = ITranscriptCueEndTimeValue(entry).value()
            doc.cue_start_time = ITranscriptCueStartTimeValue(entry).value()
            result.append(doc)
    else:
        result = ()
    return result


@interface.implementer(ITranscriptCatalog)
class TranscriptsCatalog(MetadataCatalog):

    name = TRANSCRIPTS_CATALOG
    document_interface = ITranscriptDocument

    return_fields = ('id', 'score', 'cue_end_time',
                     'cue_start_time', 'containerId')

    def index_doc(self, doc_id, value, commit=None, event=True):
        commit = self.auto_commit if commit is None else commit
        documents = _transcript_documents_creator(value)
        size = len(documents) - 1
        for x, document in enumerate(documents):
            do_commit = bool(x == size and commit)
            self._do_index(document.id, document, commit=do_commit)
        if event and documents:
            notify(ObjectIndexedEvent(value, doc_id))
        return bool(documents)

    def unindex_doc(self, doc_id, commit=None, event=True):
        commit = self.auto_commit if commit is None else commit
        # delete anything that matches that id
        q = "id:%s*" % lucene_escape(doc_id)
        self.client.delete(q=q, commit=commit)
        if event:
            obj = object_finder(doc_id)
            notify(ObjectUnindexedEvent(obj, doc_id))
            return obj
        return None

    def filter(self, event, query=None):
        packages = getattr(query, '_v_packages', None)
        packages = packages or set(getattr(query, 'packages', None) or ())
        if not hasattr('packages', '_v_packages'):
            # pylint: disable=protected-access
            query._v_packages = packages
        containers = event.get('containerId')
        if isinstance(containers, six.string_types):
            containers = containers.split()
        containers = set(containers or ())
        return not bool(   not packages
                        or not containers
                        or packages.intersection(containers))

    def build_from_search_query(self, query, **kwargs):  # pylint: disable=arguments-differ
        term, fq, params = MetadataCatalog.build_from_search_query(self, query, **kwargs)
        if 'mimeType' not in fq:
            types = self.get_mime_types(self.name)
            fq.add_or('mimeType', [lucene_escape(x) for x in types])
        return term, fq, params

    def clear(self, commit=None):
        types = self.get_mime_types(self.name)
        q = "mimeType:(%s)" % self._OR_.join(lucene_escape(x) for x in types)
        commit = self.auto_commit if commit is None else bool(commit)
        self.client.delete(q=q, commit=commit)
    reset = clear
