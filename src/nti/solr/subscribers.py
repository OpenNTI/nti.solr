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

from nti.dataserver.interfaces import IEntity
from nti.dataserver.interfaces import IUserGeneratedData
from nti.dataserver.interfaces import IDeletedObjectPlaceholder

from nti.solr import ENTITIES_QUEUE
from nti.solr import USERDATA_QUEUE
from nti.solr import EVALUATIONS_QUEUE
from nti.solr import CONTENT_UNITS_QUEUE

from nti.solr.interfaces import IIndexObjectEvent

from nti.solr.common import queue_add
from nti.solr.common import queue_remove
from nti.solr.common import queue_modified
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
	queue_remove(USERDATA_QUEUE, 
				 single_unindex_job,
				 obj=obj)

# Entity subscribers
@component.adapter(IEntity, IIntIdAddedEvent)
def _entity_added(obj, event):
	queue_add(ENTITIES_QUEUE, single_index_job, obj)

@component.adapter(IEntity, IObjectModifiedEvent)
def _entity_modified(obj, event):
	queue_modified(ENTITIES_QUEUE, single_index_job, obj)

@component.adapter(IEntity, IIntIdRemovedEvent)
def _entity_removed(obj, event):
	queue_remove(ENTITIES_QUEUE, 
				 single_unindex_job,
				 obj=obj)

# Content units subscribers
@component.adapter(IContentUnit, IIntIdAddedEvent)
def _contentunit_added(obj, event=None):
	queue_add(CONTENT_UNITS_QUEUE, single_index_job, obj)

@component.adapter(IContentUnit, IObjectModifiedEvent)
def _contentunit_modified(obj, event):
	queue_modified(CONTENT_UNITS_QUEUE, single_index_job, obj)

@component.adapter(IContentUnit, IIntIdRemovedEvent)
def _contentunit_removed(obj, event):
	queue_remove(CONTENT_UNITS_QUEUE, 
				 single_unindex_job,
				 obj=obj)

@component.adapter(IContentUnit, IIndexObjectEvent)
def _index_contentunit(obj, event):
	_contentunit_added(obj, None)
	
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
