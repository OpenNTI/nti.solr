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
from hamcrest import ends_with
from hamcrest import has_entries
from hamcrest import has_items
from hamcrest import has_properties
from hamcrest import contains_inanyorder

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans
import nti.dataserver.tests.mock_dataserver as mock_dataserver

from nti.solr.calendar.tests import HAS_CALENDAR

from nti.solr.tests import SOLRTestLayer

@unittest.skipIf(not HAS_CALENDAR, "")
class TestSubscribers(unittest.TestCase):

    layer = SOLRTestLayer

    @WithMockDSTrans
    @fudge.patch('nti.solr.common.get_job_queue')
    def test_events(self, mock_queue):
        from nti.contenttypes.calendar.model import Calendar
        from nti.contenttypes.calendar.model import CalendarEvent
        from nti.solr.calendar import CALENDAR_EVENTS_QUEUE
        from nti.solr.interfaces import IIDValue

        class _MockQueue(object):
            def put(self, job):
                jobs = getattr(self, 'jobs', None)
                if jobs is None:
                    jobs = self.jobs = []
                jobs.append(job)
                return job
        queue = _MockQueue()
        mock_queue.is_callable().with_args(CALENDAR_EVENTS_QUEUE).returns(queue)

        # add
        calendar = Calendar(title=u'study')
        mock_dataserver.current_transaction.add(calendar)
        event = calendar.store_event(CalendarEvent(title=u"english"))
        source = IIDValue(event).value()

        assert_that(queue.jobs, has_length(1))
        job = queue.jobs.pop()
        assert_that(job.id, ends_with('_added'))
        assert_that(job._callable_root.__name__, is_('single_index_job'))
        assert_that(job.kwargs, has_entries({'core': 'calendarevents',
                                             'site': 'dataserver2',
                                             'source': source}))

        # remove
        calendar.remove_event(event)
        assert_that(queue.jobs, has_length(1))
        job = queue.jobs.pop()
        assert_that(job.id, ends_with('_removed'))
        assert_that(job._callable_root.__name__, is_('single_unindex_job'))
        assert_that(job.kwargs, has_entries({'core': 'calendarevents',
                                             'site': 'dataserver2',
                                             'source': source}))
