#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from nti.schema.field import ValidDatetime
from nti.schema.field import Text as ValidText
from nti.schema.field import DecodingValidTextLine as ValidTextLine

from nti.solr.interfaces import tagField
from nti.solr.interfaces import IDateField
from nti.solr.interfaces import ITextField
from nti.solr.interfaces import INTIIDValue
from nti.solr.interfaces import ITitleValue
from nti.solr.interfaces import ISuggestField
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import IAttributeValue
from nti.solr.interfaces import IMetadataDocument


class ICalendarEventLocationValue(IAttributeValue):
    """
    Adapter interface to get the calendar event location.
    """


class ICalendarEventStartTimeValue(IAttributeValue):
    """
    Adapter interface to get the calendar event start time.
    """


class ICalendarEventEndTimeValue(IAttributeValue):
    """
    Adapter interface to get the calendar event end time.
    """


class ICalendarEventDocument(IMetadataDocument):

    ntiid = ValidTextLine(title=u'calendar event ntiid', required=False)

    title_en = ValidTextLine(title=u'Title to index', required=False)

    content_en = ValidText(title=u'Description to index', required=False)

    location = ValidTextLine(title=u'The location', required=False)

    event_start_time = ValidDatetime(title=u"The start date", required=False)

    event_end_time = ValidDatetime(title=u"The end date", required=False)


tagField(ICalendarEventDocument['ntiid'], True, INTIIDValue)

tagField(ICalendarEventDocument['title_en'], True, ITitleValue,
         type_=u'text_lower',
         provided=ITextField)

tagField(ICalendarEventDocument['content_en'], True, IContentValue,
         type_=u'text_lower',
         provided=(ITextField, ISuggestField))

tagField(ICalendarEventDocument['location'], True, ICalendarEventLocationValue,
         type_=u'text_lower',
         provided=ITextField)

tagField(ICalendarEventDocument['event_start_time'], True, ICalendarEventStartTimeValue,
         provided=IDateField)

tagField(ICalendarEventDocument['event_end_time'], True, ICalendarEventEndTimeValue,
         provided=IDateField)
