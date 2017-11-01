#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_in
from hamcrest import is_not
from hamcrest import assert_that

from nti.testing.matchers import is_empty

import unittest

from nti.solr.userdata import USERDATA_CATALOG

from nti.solr.tests import SOLRTestLayer

from nti.solr.utils import mimeTypeRegistry


class TestInterfaces(unittest.TestCase):

    layer = SOLRTestLayer

    def test_mimetypes(self):
        assert_that(mimeTypeRegistry.get_mime_types(USERDATA_CATALOG),
                    is_not(is_empty()))

    def test_queue_name(self):
        from nti.solr.userdata import USERDATA_QUEUE
        from nti.solr import QUEUE_NAMES
        assert_that(USERDATA_QUEUE, is_in(QUEUE_NAMES))
