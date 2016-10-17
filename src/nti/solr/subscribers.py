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

from nti.async import create_job

from nti.dataserver.interfaces import IUserGeneratedData
from nti.dataserver.interfaces import IDeletedObjectPlaceholder

from nti.solr import get_factory
from nti.solr import USER_DATA_QUEUE

def get_job_queue(name):
	factory = get_factory()
	return factory.get_queue(name)

def add_2_queue(name, obj):
	pass

def queue_added(name, obj, **kwargs):
	queue = get_job_queue(name)
	job = create_job(None, obj, **kwargs)
	queue.put(job)

def queue_modified(name, obj):
	pass

def queue_remove(name, obj):
	pass

@component.adapter(IUserGeneratedData, IIntIdAddedEvent)
def _user_data_added(obj, event):
	queue_added(USER_DATA_QUEUE, obj)

@component.adapter(IUserGeneratedData, IObjectModifiedEvent)
def _user_data_modified(obj, event):
	if IDeletedObjectPlaceholder.providedBy(obj):
		queue_remove(USER_DATA_QUEUE, obj)
	else:
		queue_modified(USER_DATA_QUEUE, obj)

@component.adapter(IUserGeneratedData, IIntIdRemovedEvent)
def _user_data_removed(obj, event):
	queue_remove(USER_DATA_QUEUE, obj)
