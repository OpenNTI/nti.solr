#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

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

from zope import component

from nti.externalization import to_external_object

from nti.solr.calendar.tests import HAS_CALENDAR

from nti.solr.tests import SOLRTestLayer

@unittest.skipIf(not HAS_CALENDAR, "")
class TestModel(unittest.TestCase):

    layer = SOLRTestLayer

    def test_calendar_event_document(self):
        from nti.solr.calendar.model import CalendarEventDocument
        document = CalendarEventDocument(title_en=u'abc',
                                         content_en=u'you',
                                         location=u'3620',
                                         event_start_time=datetime.utcfromtimestamp(1575986400),
                                         event_end_time=datetime.utcfromtimestamp(1576018800),
                                         ntiid=u'tag:nextthought.com,2011-10:alex@nextthought.com-OID-0xe3d3:5573657273:gEZkDFFAPk3')
        expected_keys = ('mimeType', 'title_en', 'content_en', 'location', 'event_start_time', 'event_end_time', 'ntiid')

        external = to_external_object(document)
        assert_that(external, has_entries({'MimeType': 'application/vnd.nextthought.solr.calendareventdocument',
                                           'title_en': 'abc',
                                           'content_en': 'you',
                                           'location': '3620',
                                           'event_start_time': '2019-12-10T14:00:00Z',
                                           'event_end_time': '2019-12-10T23:00:00Z',
                                           'ntiid': 'tag:nextthought.com,2011-10:alex@nextthought.com-OID-0xe3d3:5573657273:gEZkDFFAPk3'}))
        assert_that(external.keys(), has_items(*expected_keys))
        assert_that(len(external.keys()) > len(expected_keys), is_(True))

        external = to_external_object(document, name='solr')
        assert_that(external, has_entries({'mimeType': 'application/vnd.nextthought.solr.calendareventdocument',
                                           'title_en': 'abc',
                                           'content_en': 'you',
                                           'location': '3620',
                                           'event_start_time': '2019-12-10T14:00:00Z',
                                           'event_end_time': '2019-12-10T23:00:00Z',
                                           'ntiid': 'tag:nextthought.com,2011-10:alex@nextthought.com-OID-0xe3d3:5573657273:gEZkDFFAPk3'}))
        assert_that(external.keys(), contains_inanyorder(*expected_keys))

    def test_utility(self):
        from nti.solr.interfaces import ICalendarEventCatalog
        from nti.solr.calendar.model import CalendarEventCatalog
        catalog = component.getUtility(ICalendarEventCatalog, name='calendarevents')
        assert_that(catalog, instance_of(CalendarEventCatalog))
