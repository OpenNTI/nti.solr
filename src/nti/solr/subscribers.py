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

from nti.dataserver.interfaces import IEntity
from nti.dataserver.interfaces import IUserGeneratedData
from nti.dataserver.interfaces import IDeletedObjectPlaceholder

from nti.solr import ENTITIES_QUEUE
from nti.solr import USERDATA_QUEUE
from nti.solr import EVALUATIONS_QUEUE

from nti.solr.common import queue_add
from nti.solr.common import queue_remove
from nti.solr.common import queue_modified
from nti.solr.common import single_index_job
from nti.solr.common import single_unindex_job

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

# Don't include assessment imports in case the assessment pkg is not available
def _evaluation_added(obj, event):
	queue_add(EVALUATIONS_QUEUE, single_index_job, obj)

def _evaluation_modified(obj, event):
	queue_modified(EVALUATIONS_QUEUE, single_index_job, obj)

def _evaluation_removed(obj, event):
	queue_remove(EVALUATIONS_QUEUE, 
				 single_unindex_job,
				 obj=obj)
