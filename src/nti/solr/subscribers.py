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

from nti.dataserver.interfaces import IUserGeneratedData
from nti.dataserver.interfaces import IDeletedObjectPlaceholder

from nti.solr import USER_DATA_QUEUE

from nti.solr.common import queue_add
from nti.solr.common import queue_remove
from nti.solr.common import queue_modified
from nti.solr.common import single_index_job
from nti.solr.common import single_unindex_job

from nti.solr.interfaces import ICoreCatalog

@component.adapter(IUserGeneratedData, IIntIdAddedEvent)
def _user_data_added(obj, event):
	queue_add(USER_DATA_QUEUE, single_index_job, obj)

@component.adapter(IUserGeneratedData, IObjectModifiedEvent)
def _user_data_modified(obj, event):
	if IDeletedObjectPlaceholder.providedBy(obj):
		queue_remove(USER_DATA_QUEUE, single_unindex_job, obj)
	else:
		queue_modified(USER_DATA_QUEUE, single_index_job, obj)

@component.adapter(IUserGeneratedData, IIntIdRemovedEvent)
def _user_data_removed(obj, event):
	catalog = ICoreCatalog(obj, None)
	if catalog is not None:
		queue_remove(USER_DATA_QUEUE, 
					 single_unindex_job,
					 obj=obj,
					 core=catalog.name)
