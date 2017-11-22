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

from nti.base.interfaces import IDict

from nti.contentsearch.interfaces import ISearchHit
from nti.contentsearch.interfaces import IResultTransformer
from nti.contentsearch.interfaces import ITranscriptSearchHit
from nti.contentsearch.interfaces import IContentUnitSearchHit
from nti.contentsearch.interfaces import IUserGeneratedDataSearchHit

from nti.contentsearch.search_hits import SearchHit
from nti.contentsearch.search_hits import TranscriptSearchHit
from nti.contentsearch.search_hits import ContentUnitSearchHit
from nti.contentsearch.search_hits import UserGeneratedDataSearchHit

from nti.contenttypes.presentation.interfaces import INTITranscript

from nti.dataserver.interfaces import IUserGeneratedData

from nti.solr.interfaces import INTIIDValue
from nti.solr.interfaces import IStringValue
from nti.solr.interfaces import ICreatorValue
from nti.solr.interfaces import IMimeTypeValue
from nti.solr.interfaces import IContainersValue
from nti.solr.interfaces import ILastModifiedValue
from nti.solr.interfaces import IContainerContextValue

logger = __import__('logging').getLogger(__name__)


@component.adapter(basestring)
@interface.implementer(IStringValue)
class _StringValue(object):

    def __init__(self, context=None):
        self.context = context

    def lang(self, unused_context):
        return 'en'

    def value(self, context=None):
        context = self.context if context is None else context
        return text_(context) if context else None

HIT_FIELDS = ((INTIIDValue, 'NTIID'),
              (ICreatorValue, 'Creator'),
              (IContainersValue, 'Containers'),
              (IMimeTypeValue, 'TargetMimeType'),
              (ILastModifiedValue, 'lastModified'),
              (IContainerContextValue, 'ContainerContext'))


@interface.implementer(ISearchHit)
@component.adapter(interface.Interface, IDict)
def default_search_hit_adapter(obj, result, hit=None):
    hit = SearchHit() if hit is None else hit
    # set required fields
    hit.Target = obj
    hit.ID = result['id']
    hit.Score = result['score']
    # set extra fields
    for value_interface, name in HIT_FIELDS:
        adapted = value_interface(obj, None)
        if adapted is not None:
            value = adapted.value()
            if value is not None:
                setattr(hit, name, value)
    return hit
_default_search_hit_adapter = default_search_hit_adapter


@interface.implementer(ITranscriptSearchHit)
@component.adapter(INTITranscript, IDict)
def _transcript_search_hit_adapter(obj, result):
    hit = default_search_hit_adapter(obj, result, TranscriptSearchHit())
    hit.EndMilliSecs = result['cue_end_time']
    hit.StartMilliSecs = result['cue_start_time']
    return hit


@interface.implementer(IContentUnitSearchHit)
def _contentunit_search_hit_adapter(obj, result):
    return default_search_hit_adapter(obj, result, ContentUnitSearchHit())


@component.adapter(IUserGeneratedData, IDict)
@interface.implementer(IUserGeneratedDataSearchHit)
def ugd_search_hit_adapter(obj, result):
    return default_search_hit_adapter(obj, result, UserGeneratedDataSearchHit())


@component.adapter(INTITranscript)
@interface.implementer(IResultTransformer)
def transcript_to_media(obj):
    return obj.__parent__
