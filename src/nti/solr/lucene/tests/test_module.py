#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import is_not
from hamcrest import assert_that
does_not = is_not

import unittest

from nti.solr.lucene import is_valid_query
from nti.solr.lucene import is_phrase_search

from nti.solr.tests import SOLRTestLayer


class TestLucer(unittest.TestCase):

    layer = SOLRTestLayer

    def test_is_valid_query(self):
        assert_that(is_valid_query('ichigo'), is_(True))
        assert_that(is_valid_query('&*E%#'), is_(False))
        
    def test_is_phrase_search(self):
        assert_that(is_phrase_search('ichigo'), is_(False))
        assert_that(is_phrase_search('"Aizen"'), is_(True))
