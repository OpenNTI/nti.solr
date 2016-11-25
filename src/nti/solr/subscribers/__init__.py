#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from zope.intid.interfaces import IIntIdAddedEvent
from zope.intid.interfaces import IIntIdRemovedEvent

from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from nti.contenttypes.presentation.interfaces import INTIMedia
from nti.contenttypes.presentation.interfaces import INTITranscript
from nti.contenttypes.presentation.interfaces import INTIDocketAsset
from nti.contenttypes.presentation.interfaces import IPresentationAsset
from nti.contenttypes.presentation.interfaces import IPresentationAssetMovedEvent

from nti.dataserver.interfaces import IEntity
from nti.dataserver.interfaces import IUserGeneratedData
from nti.dataserver.interfaces import IDeletedObjectPlaceholder

from nti.solr import ASSETS_QUEUE
from nti.solr import COURSES_QUEUE
from nti.solr import USERDATA_QUEUE
from nti.solr import EVALUATIONS_QUEUE
from nti.solr import TRANSCRIPTS_QUEUE

from nti.solr.interfaces import IIndexObjectEvent
from nti.solr.interfaces import IUnindexObjectEvent

from nti.solr.common import queue_add
from nti.solr.common import add_to_queue
from nti.solr.common import queue_remove
from nti.solr.common import queue_modified
from nti.solr.common import delete_user_data
from nti.solr.common import single_index_job
from nti.solr.common import single_unindex_job

# UGD subscribers
@component.adapter(IUserGeneratedData, IIntIdAddedEvent)
def _userdata_added(obj, event):
	queue_add(USERDATA_QUEUE, single_index_job, obj)

@component.adapter(IUserGeneratedData, IObjectModifiedEvent)
def _userdata_modified(obj, event):
	if IDeletedObjectPlaceholder.providedBy(obj):
		queue_remove(USERDATA_QUEUE, single_unindex_job, obj)
	else:
		queue_modified(USERDATA_QUEUE, single_index_job, obj)

@component.adapter(IUserGeneratedData, IIntIdRemovedEvent)
def _userdata_removed(obj, event):
	queue_remove(USERDATA_QUEUE, single_unindex_job, obj=obj)

@component.adapter(IUserGeneratedData, IIndexObjectEvent)
def _index_userdata(obj, event):
	queue_add(obj, None)

@component.adapter(IUserGeneratedData, IUnindexObjectEvent)
def _unindex_userdata(obj, event):
	queue_remove(obj, None)

# Assets subscribers

@component.adapter(INTITranscript, IIndexObjectEvent)
def _index_transcript(obj, event):
	queue_add(TRANSCRIPTS_QUEUE, single_index_job, obj)

@component.adapter(INTITranscript, IUnindexObjectEvent)
def _unindex_transcript(obj, event):
	queue_add(TRANSCRIPTS_QUEUE, single_unindex_job, obj)

@component.adapter(IPresentationAsset, IIntIdAddedEvent)
def _asset_added(obj, event=None):
	if INTIMedia.providedBy(obj) or INTIDocketAsset.providedBy(obj):
		queue_add(ASSETS_QUEUE, single_index_job, obj)
	if INTIMedia.providedBy(obj):
		for transcript in getattr(obj, 'transcripts', None) or ():
			_index_transcript(transcript, None)

@component.adapter(IPresentationAsset, IObjectModifiedEvent)
def _asset_modified(obj, event):
	if INTIMedia.providedBy(obj) or INTIDocketAsset.providedBy(obj):
		queue_modified(ASSETS_QUEUE, single_index_job, obj)
	if INTIMedia.providedBy(obj):
		for transcript in getattr(obj, 'transcripts', None) or ():
			_index_transcript(transcript, None)

@component.adapter(IPresentationAsset, IIntIdRemovedEvent)
def _asset_removed(obj, event):
	if INTIMedia.providedBy(obj) or INTIDocketAsset.providedBy(obj):
		queue_remove(ASSETS_QUEUE, single_unindex_job, obj=obj)
	if INTIMedia.providedBy(obj):
		for transcript in getattr(obj, 'transcripts', None) or ():
			queue_remove(TRANSCRIPTS_QUEUE, single_unindex_job, obj=transcript)

@component.adapter(IPresentationAsset, IPresentationAssetMovedEvent)
def _asset_moved(obj, event):
	if INTIMedia.providedBy(obj) or INTIDocketAsset.providedBy(obj):
		queue_modified(ASSETS_QUEUE, single_index_job, obj=obj)

@component.adapter(IPresentationAsset, IIndexObjectEvent)
def _index_asset(obj, event):
	_asset_added(obj, None)

@component.adapter(IPresentationAsset, IUnindexObjectEvent)
def _unindex_asset(obj, event):
	_asset_removed(obj, None)

# Evaluation subscribers
# XXX. Don't include assessment imports in case the assessment pkg is not available
def _evaluation_added(obj, event):
	if obj.isPublished():
		queue_add(EVALUATIONS_QUEUE, single_index_job, obj)

def _evaluation_modified(obj, event):
	if obj.isPublished():
		queue_modified(EVALUATIONS_QUEUE, single_index_job, obj)

def _evaluation_published(obj, event):
	queue_modified(EVALUATIONS_QUEUE, single_index_job, obj)

def _evaluation_unpublished(obj, event):
	queue_remove(EVALUATIONS_QUEUE, single_unindex_job, obj=obj)

def _evaluation_removed(obj, event):
	queue_remove(EVALUATIONS_QUEUE, single_unindex_job, obj=obj)

def _index_evaluation(obj, event):
	queue_add(EVALUATIONS_QUEUE, single_index_job, obj)

def _unindex_evaluation(obj, event):
	_evaluation_removed(obj, None)

# Course subscribers
# XXX. Don't include course imports in case the course pkg is not available
def _course_added(obj, event):
	queue_add(COURSES_QUEUE, single_index_job, obj)

def _course_modified(obj, event):
	queue_modified(COURSES_QUEUE, single_index_job, obj)

def _course_removed(obj, event):
	queue_remove(COURSES_QUEUE, single_unindex_job, obj=obj)

def _index_course(obj, event):
	_course_added(obj, None)

def _unindex_course(obj, event):
	queue_remove(obj, None)
