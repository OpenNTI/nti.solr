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

from nti.dataserver.interfaces import IUserGeneratedData
from nti.dataserver.interfaces import IDeletedObjectPlaceholder

from nti.solr.interfaces import IIndexObjectEvent
from nti.solr.interfaces import IUnindexObjectEvent

from nti.solr.common import queue_add
from nti.solr.common import queue_remove
from nti.solr.common import queue_modified
from nti.solr.common import single_index_job
from nti.solr.common import single_unindex_job

from nti.solr.userdata import USERDATA_QUEUE

logger = __import__('logging').getLogger(__name__)


@component.adapter(IUserGeneratedData, IIntIdAddedEvent)
def _userdata_added(obj, unused_event=None):
    queue_add(USERDATA_QUEUE, single_index_job, obj)
userdata_added = _userdata_added


@component.adapter(IUserGeneratedData, IObjectModifiedEvent)
def _userdata_modified(obj, unused_event=None):
    if IDeletedObjectPlaceholder.providedBy(obj):
        queue_remove(USERDATA_QUEUE, single_unindex_job, obj)
    else:
        queue_modified(USERDATA_QUEUE, single_index_job, obj)


@component.adapter(IUserGeneratedData, IIntIdRemovedEvent)
def _userdata_removed(obj, unused_event=None):
    queue_remove(USERDATA_QUEUE, single_unindex_job, obj=obj)


@component.adapter(IUserGeneratedData, IIndexObjectEvent)
def _index_userdata(obj, unused_event=None):
    _userdata_added(obj, None)
index_userdata = _index_userdata


@component.adapter(IUserGeneratedData, IUnindexObjectEvent)
def _unindex_userdata(obj, unused_event=None):
    _userdata_removed(obj, None)
