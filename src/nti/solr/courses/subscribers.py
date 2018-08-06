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

from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry
from nti.contenttypes.courses.interfaces import ICourseInstanceImportedEvent

from nti.solr.common import queue_add
from nti.solr.common import queue_remove
from nti.solr.common import queue_modified
from nti.solr.common import single_index_job
from nti.solr.common import single_unindex_job

from nti.solr.courses import COURSES_QUEUE

from nti.solr.interfaces import IIndexObjectEvent
from nti.solr.interfaces import IUnindexObjectEvent

logger = __import__('logging').getLogger(__name__)


@component.adapter(ICourseInstance, IIntIdAddedEvent)
def _course_added(obj, unused_event=None):
    queue_add(COURSES_QUEUE, single_index_job, obj)


@component.adapter(ICourseInstance, IObjectModifiedEvent)
@component.adapter(ICourseCatalogEntry, IObjectModifiedEvent)
def _course_modified(obj, unused_event=None):
    course = ICourseInstance(obj)
    queue_modified(COURSES_QUEUE, single_index_job, course)


@component.adapter(ICourseInstance, ICourseInstanceImportedEvent)
def _course_imported(obj, unused_event=None):
    queue_modified(COURSES_QUEUE, single_index_job, obj)


@component.adapter(ICourseInstance, IIntIdRemovedEvent)
def _course_removed(obj, unused_event=None):
    queue_remove(COURSES_QUEUE, single_unindex_job, obj=obj)


@component.adapter(ICourseInstance, IIndexObjectEvent)
def _index_course(obj, unused_event=None):
    _course_added(obj, None)


@component.adapter(ICourseInstance, IUnindexObjectEvent)
def _unindex_course(obj, unused_event=None):
    _course_removed(obj, None)
