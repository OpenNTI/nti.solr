#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from dolmen.builtins.interfaces import IDict

from zope import component
from zope import interface

from nti.common.string import to_unicode

from nti.contentsearch.interfaces import ISearchHit
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


@component.adapter(basestring)
@interface.implementer(IStringValue)
class _StringValue(object):

    def __init__(self, context=None):
        self.context = context

    def lang(self, context):
        return 'en'

    def value(self, context=None):
        context = self.context if context is None else context
        return to_unicode(context) if context else None

HIT_FIELDS = ((INTIIDValue, 'NTIID'),
              (ICreatorValue, 'Creator'),
              (IContainersValue, 'Containers'),
              (IMimeTypeValue, 'TargetMimeType'),
              (ILastModifiedValue, 'lastModified'),
              (IContainerContextValue, 'ContainerContext'))


@interface.implementer(ISearchHit)
@component.adapter(interface.Interface, IDict)
def _default_search_hit_adapter(obj, result, hit=None):
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


@interface.implementer(ITranscriptSearchHit)
@component.adapter(INTITranscript, IDict)
def _transcript_search_hit_adapter(obj, result):
    hit = _default_search_hit_adapter(obj, result, TranscriptSearchHit())
    hit.EndMilliSecs = result['cue_end_time']
    hit.StartMilliSecs = result['cue_start_time']
    return hit


@interface.implementer(IContentUnitSearchHit)
def _contentunit_search_hit_adapter(obj, result):
    return _default_search_hit_adapter(obj, result, ContentUnitSearchHit())


@component.adapter(IUserGeneratedData, IDict)
@interface.implementer(IUserGeneratedDataSearchHit)
def ugd_search_hit_adapter(obj, result):
    return _default_search_hit_adapter(obj, result, UserGeneratedDataSearchHit())
