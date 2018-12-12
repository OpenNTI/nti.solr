#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import fudge

import unittest

from datetime import datetime

from hamcrest import is_
from hamcrest import is_in
from hamcrest import not_none
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_entries
from hamcrest import has_items
from hamcrest import instance_of
from hamcrest import has_properties
from hamcrest import contains_inanyorder

from nti.solr.calendar.tests import HAS_CALENDAR

from nti.solr.tests import SOLRTestLayer

@unittest.skipIf(not HAS_CALENDAR, "")
class TestAdapters(unittest.TestCase):

    layer = SOLRTestLayer

    @fudge.patch('nti.solr.metadata.getSite')
    def test_adapters(self, fake_site):
        class _MockSite(object):
            __name__ = u'test.dev'
        fake_site.is_callable().returns(_MockSite())
        from nti.solr.interfaces import ITitleValue
        from nti.solr.interfaces import IContentValue
        from nti.solr.calendar.interfaces import ICalendarEventDocument
        from nti.solr.calendar.interfaces import ICalendarEventEndTimeValue
        from nti.solr.calendar.interfaces import ICalendarEventLocationValue
        from nti.solr.calendar.interfaces import ICalendarEventStartTimeValue

        from nti.contenttypes.calendar.model import CalendarEvent
        obj = CalendarEvent(title=u'abc',
                            description=u'you',
                            location=u'3620',
                            start_time=datetime.utcfromtimestamp(1575986400),
                            end_time=datetime.utcfromtimestamp(1576018800))
        assert_that(ITitleValue(obj).value(), is_('abc'))
        assert_that(IContentValue(obj).value(), is_('you'))
        assert_that(ICalendarEventLocationValue(obj).value(), is_('3620'))
        assert_that(ICalendarEventStartTimeValue(obj).value().strftime('%Y-%m-%dT%H:%M:%SZ'), is_('2019-12-10T14:00:00Z'))
        assert_that(ICalendarEventEndTimeValue(obj).value().strftime('%Y-%m-%dT%H:%M:%SZ'), is_('2019-12-10T23:00:00Z'))

        doc = ICalendarEventDocument(obj)
        assert_that(doc, has_properties({'title_en': 'abc',
                                         'content_en': 'you',
                                         'location': '3620',
                                         'event_start_time': not_none(),
                                         'event_end_time': not_none()}))
        assert_that(doc.event_start_time.strftime('%Y-%m-%dT%H:%M:%SZ'), is_('2019-12-10T14:00:00Z'))
        assert_that(doc.event_end_time.strftime('%Y-%m-%dT%H:%M:%SZ'), is_('2019-12-10T23:00:00Z'))

        from nti.solr.interfaces import ICoreCatalog
        from nti.solr.calendar.model import CalendarEventCatalog
        catalog = ICoreCatalog(obj)
        assert_that(catalog, instance_of(CalendarEventCatalog))
