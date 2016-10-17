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

from nti.solr import get_factory

def get_job_queue(name):
    factory = get_factory()
    return factory.get_queue(name)

def add_2_queue(queue_name, obj):
    pass

def queue_added(obj):
    try:
        return add_2_queue(obj)
    except TypeError:
        pass
    return False

def queue_modified(obj):
    pass

def queue_remove(obj):
    pass

@component.adapter(IUserGeneratedData, IIntIdAddedEvent)
def _user_data_added(modeled, event):
    queue_added(modeled)

@component.adapter(IUserGeneratedData, IObjectModifiedEvent)
def _user_data_modified(obj, event):
    if IDeletedObjectPlaceholder.providedBy(obj):
        queue_remove(obj)
    else:
        queue_modified(obj)

@component.adapter(IUserGeneratedData, IIntIdRemovedEvent)
def _user_data_removed(obj, event):
    queue_remove(obj)
