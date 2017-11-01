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

from nti.solr.tests import SOLRTestLayer

from nti.solr.utils import mimeTypeRegistry


class TestInterfaces(unittest.TestCase):

    layer = SOLRTestLayer

    def test_mimetypes(self):
        from nti.solr.entities import ENTITIES_CATALOG
        assert_that(mimeTypeRegistry.get_mime_types(ENTITIES_CATALOG),
                    has_length(4))
        
    def test_queue_name(self):
        from nti.solr.entities import ENTITIES_QUEUE
        from nti.solr import QUEUE_NAMES
        assert_that(ENTITIES_QUEUE, is_in(QUEUE_NAMES))
