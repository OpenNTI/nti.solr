#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component

from zope.intid.interfaces import IIntIdAddedEvent
from zope.intid.interfaces import IIntIdRemovedEvent

from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from nti.dataserver.interfaces import IEntity

from nti.solr.entities import ENTITIES_QUEUE

from nti.solr.interfaces import IIndexObjectEvent
from nti.solr.interfaces import IUnindexObjectEvent

from nti.solr.common import queue_add
from nti.solr.common import add_to_queue
from nti.solr.common import queue_remove
from nti.solr.common import queue_modified
from nti.solr.common import delete_user_data
from nti.solr.common import single_index_job
from nti.solr.common import single_unindex_job

from nti.solr.userdata import USERDATA_QUEUE

logger = __import__('logging').getLogger(__name__)


@component.adapter(IEntity, IIntIdAddedEvent)
def _entity_added(obj, unused_event=None):
    queue_add(ENTITIES_QUEUE, single_index_job, obj)


@component.adapter(IEntity, IObjectModifiedEvent)
def _entity_modified(obj, unused_event=None):
    queue_modified(ENTITIES_QUEUE, single_index_job, obj)


@component.adapter(IEntity, IIntIdRemovedEvent)
def _entity_removed(obj, unused_event=None):
    queue_remove(ENTITIES_QUEUE, single_unindex_job, obj=obj)
    add_to_queue(USERDATA_QUEUE, delete_user_data, obj=obj,
                 jid='userdata_removal', username=obj.username)


@component.adapter(IEntity, IIndexObjectEvent)
def _index_entity(obj, unused_event=None):
    _entity_added(obj, None)


@component.adapter(IEntity, IUnindexObjectEvent)
def _unindex_entity(obj, unused_event=None):
    queue_remove(ENTITIES_QUEUE, single_unindex_job, obj=obj)
