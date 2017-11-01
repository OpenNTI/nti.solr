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

from nti.solr.assessment.tests import HAS_ASSESMENT

from nti.solr.tests import SOLRTestLayer

from nti.solr.utils import mimeTypeRegistry


@unittest.skipIf(not HAS_ASSESMENT, "")
class TestInterfaces(unittest.TestCase):

    layer = SOLRTestLayer

    def test_mimetypes(self):
        from nti.assessment.interfaces import ALL_EVALUATION_MIME_TYPES
        from nti.solr.assessment import EVALUATIONS_CATALOG

        for mimeType in ALL_EVALUATION_MIME_TYPES:
            assert_that(mimeTypeRegistry.get_catalog(mimeType),
                        is_(EVALUATIONS_CATALOG))
        assert_that(mimeTypeRegistry.get_mime_types(EVALUATIONS_CATALOG),
                    has_length(len(ALL_EVALUATION_MIME_TYPES)))

    def test_queue_name(self):
        from nti.solr.assessment import EVALUATIONS_QUEUE
        from nti.solr import QUEUE_NAMES
        assert_that(EVALUATIONS_QUEUE, is_in(QUEUE_NAMES))
