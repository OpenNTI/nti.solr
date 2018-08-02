#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component

from zope.intid.interfaces import IIntIdRemovedEvent

from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from zc.intid.interfaces import IAfterIdAddedEvent

from nti.contenttypes.presentation.interfaces import IAssetRef
from nti.contenttypes.presentation.interfaces import INTIMedia
from nti.contenttypes.presentation.interfaces import INTITranscript
from nti.contenttypes.presentation.interfaces import INTIDocketAsset
from nti.contenttypes.presentation.interfaces import IPresentationAsset
from nti.contenttypes.presentation.interfaces import IAssetTitleDescribed
from nti.contenttypes.presentation.interfaces import IUserCreatedTranscript
from nti.contenttypes.presentation.interfaces import IPresentationAssetMovedEvent

from nti.solr.interfaces import IIndexObjectEvent
from nti.solr.interfaces import IUnindexObjectEvent

from nti.solr.common import queue_add
from nti.solr.common import queue_remove
from nti.solr.common import queue_modified
from nti.solr.common import single_index_job
from nti.solr.common import single_unindex_job

from nti.solr.presentation import ASSETS_QUEUE
from nti.solr.presentation import TRANSCRIPTS_QUEUE

logger = __import__('logging').getLogger(__name__)


@component.adapter(INTITranscript, IIndexObjectEvent)
def _index_transcript(obj, unused_event=None):
    queue_add(TRANSCRIPTS_QUEUE, single_index_job, obj)


@component.adapter(INTITranscript, IUnindexObjectEvent)
def _unindex_transcript(obj, unused_event=None):
    queue_remove(TRANSCRIPTS_QUEUE, single_unindex_job, obj)


@component.adapter(INTITranscript, IObjectAddedEvent)
def _index_transcript_added(obj, unused_event=None):
    if IUserCreatedTranscript.providedBy(obj):
        queue_add(TRANSCRIPTS_QUEUE, single_index_job, obj)


@component.adapter(INTITranscript, IObjectModifiedEvent)
def _index_transcript_modified(obj, unused_event=None):
    if IUserCreatedTranscript.providedBy(obj):
        queue_modified(TRANSCRIPTS_QUEUE, single_index_job, obj)


@component.adapter(INTITranscript, IObjectRemovedEvent)
def _index_transcript_removed(obj, unused_event=None):
    if IUserCreatedTranscript.providedBy(obj):
        queue_remove(TRANSCRIPTS_QUEUE, single_unindex_job, obj)


def is_indexable(obj):
    return   not IAssetRef.providedBy(obj) \
        and (   INTIMedia.providedBy(obj)
             or INTIDocketAsset.providedBy(obj)
             or IAssetTitleDescribed.providedBy(obj))


@component.adapter(IPresentationAsset, IAfterIdAddedEvent)
def _asset_added(obj, unused_event=None):
    if is_indexable(obj):
        queue_add(ASSETS_QUEUE, single_index_job, obj)
    if INTIMedia.providedBy(obj):
        for transcript in getattr(obj, 'transcripts', None) or ():
            _index_transcript(transcript, None)


@component.adapter(IPresentationAsset, IObjectModifiedEvent)
def _asset_modified(obj, unused_event=None):
    if is_indexable(obj):
        queue_modified(ASSETS_QUEUE, single_index_job, obj)
    if INTIMedia.providedBy(obj):
        for transcript in getattr(obj, 'transcripts', None) or ():
            if not IUserCreatedTranscript.providedBy(transcript):
                _index_transcript(transcript, None)


@component.adapter(IPresentationAsset, IIntIdRemovedEvent)
def _asset_removed(obj, unused_event=None):
    if is_indexable(obj):
        queue_remove(ASSETS_QUEUE, single_unindex_job, obj=obj)
    if INTIMedia.providedBy(obj):
        for transcript in getattr(obj, 'transcripts', None) or ():
            queue_remove(TRANSCRIPTS_QUEUE, single_unindex_job, obj=transcript)


@component.adapter(IPresentationAsset, IPresentationAssetMovedEvent)
def _asset_moved(obj, unused_event=None):
    if is_indexable(obj):
        queue_modified(ASSETS_QUEUE, single_index_job, obj=obj)


@component.adapter(IPresentationAsset, IIndexObjectEvent)
def _index_asset(obj, unused_event=None):
    _asset_added(obj, None)


@component.adapter(IPresentationAsset, IUnindexObjectEvent)
def _unindex_asset(obj, unused_event=None):
    _asset_removed(obj, None)
