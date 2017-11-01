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
from hamcrest import greater_than_or_equal_to

import unittest

from nti.solr.contentlibrary.tests import HAS_CONTENT_LIBRARY

from nti.solr.tests import SOLRTestLayer

from nti.solr.utils import mimeTypeRegistry


@unittest.skipIf(not HAS_CONTENT_LIBRARY, "")
class TestInterfaces(unittest.TestCase):

    layer = SOLRTestLayer

    def test_mimetypes(self):
        from nti.contentlibrary import ALL_CONTENT_MIMETYPES
        from nti.solr.contentlibrary import CONTENT_UNITS_CATALOG

        for mimeType in ALL_CONTENT_MIMETYPES:
            assert_that(mimeTypeRegistry.get_catalog(mimeType),
                        is_(CONTENT_UNITS_CATALOG))
        assert_that(mimeTypeRegistry.get_mime_types(CONTENT_UNITS_CATALOG),
                    has_length(greater_than_or_equal_to(len(ALL_CONTENT_MIMETYPES))))

    def test_queue_name(self):
        from nti.solr.contentlibrary import CONTENT_UNITS_QUEUE
        from nti.solr import QUEUE_NAMES
        assert_that(CONTENT_UNITS_QUEUE, is_in(QUEUE_NAMES))
