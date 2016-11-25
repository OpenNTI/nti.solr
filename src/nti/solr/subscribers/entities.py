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

from nti.solr import ENTITIES_QUEUE
from nti.solr import USERDATA_QUEUE

from nti.solr.interfaces import IIndexObjectEvent

from nti.solr.common import queue_add
from nti.solr.common import add_to_queue
from nti.solr.common import queue_remove
from nti.solr.common import queue_modified
from nti.solr.common import delete_user_data
from nti.solr.common import single_index_job
from nti.solr.common import single_unindex_job

@component.adapter(IEntity, IIntIdAddedEvent)
def _entity_added(obj, event=None):
	queue_add(ENTITIES_QUEUE, single_index_job, obj)

@component.adapter(IEntity, IObjectModifiedEvent)
def _entity_modified(obj, event):
	queue_modified(ENTITIES_QUEUE, single_index_job, obj)

@component.adapter(IEntity, IIntIdRemovedEvent)
def _entity_removed(obj, event):
	queue_remove(ENTITIES_QUEUE, single_unindex_job, obj=obj)
	add_to_queue(USERDATA_QUEUE, delete_user_data, obj=obj,
				 jid='userdata_removal', username=obj.username)

@component.adapter(IEntity, IIndexObjectEvent)
def _index_entity(obj, event):
	_entity_added(obj, None)
