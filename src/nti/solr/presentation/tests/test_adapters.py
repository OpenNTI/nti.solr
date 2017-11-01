#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import assert_that

import unittest

from nti.solr.interfaces import IIDValue

from nti.solr.presentation.tests import HAS_PRESENTATION

from nti.solr.tests import SOLRTestLayer


@unittest.skipIf(not HAS_PRESENTATION, "")
class TestAdapters(unittest.TestCase):

    layer = SOLRTestLayer

    def test_transcript(self):
        from nti.contenttypes.presentation.media import NTITranscript
        transcript = NTITranscript()
        transcript.ntiid = u"tag:nextthought.com,2011-10:NTI-NTITranscript-system_A10319BA.0"
        assert_that(IIDValue(transcript).value(),
                    is_('19701S-system-ntitranscript#tag:nextthought.com,2011-10:NTI-NTITranscript-system_A10319BA.0'))
