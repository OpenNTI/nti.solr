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

from nti.solr.utils import normalize_key

from nti.solr.tests import SOLRTestLayer


class TestUtils(unittest.TestCase):

    layer = SOLRTestLayer

    def test_normalize_key(self):
        # Content
        key = '19701S-system-renderablecontentpackage#tag:nextthought.com,2011-10:sjohnson@nextthought.com-HTML-4950716093280901324.0'
        result = normalize_key(key)
        assert_that(result, is_('tag:nextthought.com,2011-10:sjohnson@nextthought.com-HTML-4950716093280901324.0'))

        # Transcript
        key = '19701S-system-video#tag:nextthought.com,2011-10:sjohnson@nextthought.com-HTML-4950716093280901324.0=transcript-postfix'
        result = normalize_key(key)
        assert_that(result, is_('tag:nextthought.com,2011-10:sjohnson@nextthought.com-HTML-4950716093280901324.0'))

        key = '19701S-system-contentunit#tag:nextthought.com,2011-10:SYMMYS-HTML-Symmys_Text_Book.SecFiNTeaf_copy(1)'
        result = normalize_key(key)
        assert_that(result, is_('tag:nextthought.com,2011-10:SYMMYS-HTML-Symmys_Text_Book.SecFiNTeaf_copy(1)'))
