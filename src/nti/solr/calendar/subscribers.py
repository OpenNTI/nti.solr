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

from nti.contenttypes.calendar.interfaces import ICalendarEvent

from nti.solr.calendar import CALENDAR_EVENTS_QUEUE

from nti.solr.interfaces import IIndexObjectEvent
from nti.solr.interfaces import IUnindexObjectEvent

from nti.solr.common import queue_add
from nti.solr.common import queue_remove
from nti.solr.common import queue_modified
from nti.solr.common import single_index_job
from nti.solr.common import single_unindex_job

logger = __import__('logging').getLogger(__name__)


@component.adapter(ICalendarEvent, IIntIdAddedEvent)
def _calendar_event_added(obj, unused_event=None):
    queue_add(CALENDAR_EVENTS_QUEUE, single_index_job, obj)


@component.adapter(ICalendarEvent, IIntIdRemovedEvent)
def _calendar_event_removed(obj, unused_event=None):
    queue_remove(CALENDAR_EVENTS_QUEUE, single_unindex_job, obj=obj)


@component.adapter(ICalendarEvent, IObjectModifiedEvent)
def _calendar_event_modified(obj, unused_event=None):
    queue_modified(CALENDAR_EVENTS_QUEUE, single_index_job, obj)


@component.adapter(ICalendarEvent, IIndexObjectEvent)
def _index_calendar_event(obj, unused_event=None):
    _calendar_event_added(obj, None)


@component.adapter(ICalendarEvent, IUnindexObjectEvent)
def _unindex_calendar_event(obj, unused_event=None):
    _calendar_event_removed(obj, None)
