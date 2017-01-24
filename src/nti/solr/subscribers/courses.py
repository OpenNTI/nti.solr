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

from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.solr import COURSES_QUEUE

from nti.solr.common import queue_add
from nti.solr.common import queue_remove
from nti.solr.common import queue_modified
from nti.solr.common import single_index_job
from nti.solr.common import single_unindex_job

from nti.solr.interfaces import IIndexObjectEvent
from nti.solr.interfaces import IUnindexObjectEvent


@component.adapter(ICourseInstance, IIntIdAddedEvent)
def _course_added(obj, event):
    queue_add(COURSES_QUEUE, single_index_job, obj)


@component.adapter(ICourseInstance, IObjectModifiedEvent)
def _course_modified(obj, event):
    queue_modified(COURSES_QUEUE, single_index_job, obj)


@component.adapter(ICourseInstance, IIntIdRemovedEvent)
def _course_removed(obj, event):
    queue_remove(COURSES_QUEUE, single_unindex_job, obj=obj)


@component.adapter(ICourseInstance, IIndexObjectEvent)
def _index_course(obj, event):
    _course_added(obj, None)


@component.adapter(ICourseInstance, IUnindexObjectEvent)
def _unindex_course(obj, event):
    queue_remove(obj, None)
