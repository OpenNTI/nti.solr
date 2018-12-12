#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import is_in
from hamcrest import has_length
from hamcrest import assert_that

import unittest

from nti.solr.calendar.tests import HAS_CALENDAR

from nti.solr.tests import SOLRTestLayer

from nti.solr.utils import mimeTypeRegistry


@unittest.skipIf(not HAS_CALENDAR, "")
class TestCalendar(unittest.TestCase):

    layer = SOLRTestLayer

    def test_mimetypes(self):
        from nti.solr.calendar import COURSE_CALENDAR_EVENT_MIME_TYPE
        from nti.solr.calendar import CALENDAR_EVENTS_CATALOG

        assert_that(mimeTypeRegistry.get_catalog(COURSE_CALENDAR_EVENT_MIME_TYPE), is_(CALENDAR_EVENTS_CATALOG))

        assert_that(mimeTypeRegistry.get_mime_types(CALENDAR_EVENTS_CATALOG), has_length(1))

    def test_queue_name(self):
        from nti.solr.calendar import CALENDAR_EVENTS_QUEUE
        from nti.solr import QUEUE_NAMES
        assert_that(CALENDAR_EVENTS_QUEUE, is_in(QUEUE_NAMES))
