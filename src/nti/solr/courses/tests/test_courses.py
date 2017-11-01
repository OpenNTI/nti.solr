#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_in
from hamcrest import has_length
from hamcrest import assert_that

import unittest

from nti.solr.courses.tests import HAS_COURSES

from nti.solr.tests import SOLRTestLayer

from nti.solr.utils import mimeTypeRegistry


@unittest.skipIf(not HAS_COURSES, "")
class TestInterfaces(unittest.TestCase):

    layer = SOLRTestLayer

    def test_mimetypes(self):
        from nti.solr.courses import COURSES_CATALOG

        assert_that(mimeTypeRegistry.get_mime_types(COURSES_CATALOG),
                    has_length(3))
        
    def test_queue_name(self):
        from nti.solr.courses import COURSES_QUEUE
        from nti.solr import QUEUE_NAMES
        assert_that(COURSES_QUEUE, is_in(QUEUE_NAMES))
