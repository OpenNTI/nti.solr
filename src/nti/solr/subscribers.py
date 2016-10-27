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

from nti.contentlibrary.interfaces import IContentUnit
from nti.contentlibrary.interfaces import IContentPackage

from nti.contenttypes.presentation.interfaces import INTIMedia
from nti.contenttypes.presentation.interfaces import INTITranscript
from nti.contenttypes.presentation.interfaces import INTIDocketAsset
from nti.contenttypes.presentation.interfaces import IPresentationAsset

from nti.dataserver.interfaces import IEntity
from nti.dataserver.interfaces import IUserGeneratedData
from nti.dataserver.interfaces import IDeletedObjectPlaceholder

from nti.solr import ASSETS_QUEUE
from nti.solr import COURSES_QUEUE
from nti.solr import ENTITIES_QUEUE
from nti.solr import USERDATA_QUEUE
from nti.solr import EVALUATIONS_QUEUE
from nti.solr import TRANSCRIPTS_QUEUE
from nti.solr import CONTENT_UNITS_QUEUE

from nti.solr.interfaces import IIndexObjectEvent 
from nti.solr.interfaces import IUnindexObjectEvent

from nti.solr.common import queue_add
from nti.solr.common import add_2_queue
from nti.solr.common import queue_remove
from nti.solr.common import queue_modified
from nti.solr.common import single_index_job
from nti.solr.common import single_unindex_job
from nti.solr.common import index_content_package
from nti.solr.common import unindex_content_package

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

# Entity subscribers
@component.adapter(IEntity, IIntIdAddedEvent)
def _entity_added(obj, event):
	queue_add(ENTITIES_QUEUE, single_index_job, obj)

@component.adapter(IEntity, IObjectModifiedEvent)
def _entity_modified(obj, event):
	queue_modified(ENTITIES_QUEUE, single_index_job, obj)

@component.adapter(IEntity, IIntIdRemovedEvent)
def _entity_removed(obj, event):
	queue_remove(ENTITIES_QUEUE, single_unindex_job, obj=obj)

# Content units subscribers
@component.adapter(IContentUnit, IIntIdAddedEvent)
def _contentunit_added(obj, event=None):
	queue_add(CONTENT_UNITS_QUEUE, single_index_job, obj)

@component.adapter(IContentUnit, IObjectModifiedEvent)
def _contentunit_modified(obj, event):
	queue_modified(CONTENT_UNITS_QUEUE, single_index_job, obj)

@component.adapter(IContentUnit, IIntIdRemovedEvent)
def _contentunit_removed(obj, event):
	queue_remove(CONTENT_UNITS_QUEUE, single_unindex_job, obj=obj)

@component.adapter(IContentUnit, IIndexObjectEvent)
def _index_contentunit(obj, event):
	if not IContentPackage.providedBy(obj):
		_contentunit_added(obj, None)
	
@component.adapter(IContentUnit, IUnindexObjectEvent)
def _unindex_contentunit(obj, event):
	if not IContentPackage.providedBy(obj):
		_contentunit_removed(obj, None)

@component.adapter(IContentPackage, IIndexObjectEvent)
def _index_contentpackage(obj, event):
	add_2_queue(CONTENT_UNITS_QUEUE, index_content_package, obj, jid='added')

@component.adapter(IContentPackage, IUnindexObjectEvent)
def _unindex_contentpackage(obj, event):
	add_2_queue(CONTENT_UNITS_QUEUE, unindex_content_package, obj, jid='removed')

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

# Assets subscribers

@component.adapter(INTITranscript, IIndexObjectEvent)
def _index_transcript(obj, event):
	queue_add(TRANSCRIPTS_QUEUE, single_index_job, obj)

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

@component.adapter(IPresentationAsset, IIndexObjectEvent)
def _index_asset(obj, event):
	_asset_added(obj, None)

@component.adapter(IPresentationAsset, IUnindexObjectEvent)
def _unindex_asset(obj, event):
	_asset_removed(obj, None)
