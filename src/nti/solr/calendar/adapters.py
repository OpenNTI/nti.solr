#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component
from zope import interface

from nti.contenttypes.calendar.interfaces import ICalendarEvent

from nti.solr.calendar import CALENDAR_EVENTS_CATALOG

from nti.solr.calendar.interfaces import ICalendarEventDocument
from nti.solr.calendar.interfaces import ICalendarEventEndTimeValue
from nti.solr.calendar.interfaces import ICalendarEventLocationValue
from nti.solr.calendar.interfaces import ICalendarEventStartTimeValue

from nti.solr.calendar.model import CalendarEventDocument

from nti.solr.interfaces import ITitleValue
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import ICoreCatalog

from nti.solr.utils import document_creator

logger = __import__('logging').getLogger(__name__)


class _BasicAttributeValue(object):

    field = None

    def __init__(self, context=None, unused_default=None):
        self.context = context

    def value(self, context=None):
        context = self.context if context is None else context
        return getattr(context, self.field, None)


@component.adapter(ICalendarEvent)
@interface.implementer(ITitleValue)
class _DefaultTitleValue(_BasicAttributeValue):

    field = 'title'


@component.adapter(ICalendarEvent)
@interface.implementer(IContentValue)
class _DefaultContentValue(_BasicAttributeValue):

    field = 'description'


@component.adapter(ICalendarEvent)
@interface.implementer(ICalendarEventLocationValue)
class _DefaultLocationValue(_BasicAttributeValue):

    field = 'location'


@component.adapter(ICalendarEvent)
@interface.implementer(ICalendarEventStartTimeValue)
class _DefaultStartTimeValue(_BasicAttributeValue):

    field = 'start_time'


@component.adapter(ICalendarEvent)
@interface.implementer(ICalendarEventEndTimeValue)
class _DefaultEndTimeValue(_BasicAttributeValue):

    field = 'end_time'


@component.adapter(ICalendarEvent)
@interface.implementer(ICalendarEventDocument)
def _CalendarEventDocumentCreator(obj, factory=CalendarEventDocument):
    return document_creator(obj, factory=factory, provided=ICalendarEventDocument)

@component.adapter(ICalendarEvent)
@interface.implementer(ICoreCatalog)
def _calendar_event_to_catalog(unused_obj):
    return component.getUtility(ICoreCatalog, name=CALENDAR_EVENTS_CATALOG)
