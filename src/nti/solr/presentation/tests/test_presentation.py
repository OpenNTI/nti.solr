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

from nti.solr.presentation.tests import HAS_PRESENTATION

from nti.solr.tests import SOLRTestLayer

from nti.solr.utils import mimeTypeRegistry


@unittest.skipIf(not HAS_PRESENTATION, "")
class TestInterfaces(unittest.TestCase):

    layer = SOLRTestLayer

    def test_mimetypes(self):
        from nti.solr.presentation import ASSETS_CATALOG
        from nti.solr.presentation import TRANSCRIPTS_CATALOG

        assert_that(mimeTypeRegistry.get_mime_types(ASSETS_CATALOG),
                    has_length(5))
        assert_that(mimeTypeRegistry.get_mime_types(TRANSCRIPTS_CATALOG),
                    has_length(3))
        
    def test_queue_name(self):
        from nti.solr.presentation import ASSETS_QUEUE
        from nti.solr.presentation import TRANSCRIPTS_QUEUE
        from nti.solr import QUEUE_NAMES
        assert_that(ASSETS_QUEUE, is_in(QUEUE_NAMES))
        assert_that(TRANSCRIPTS_QUEUE, is_in(QUEUE_NAMES))
