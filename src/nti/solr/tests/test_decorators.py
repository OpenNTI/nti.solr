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

from nti.solr.decorators import _SearchFragmentDecorator

from nti.solr.tests import SOLRTestLayer

class TestDecorators(unittest.TestCase):

	layer = SOLRTestLayer

	def test_fragment_1(self):
		s = 'how our chemical messengers are synthesized and secreted from the secretory <em>cell</em>. Now'
		assert_that(_SearchFragmentDecorator.split_and_sanitize(s), is_(s))
		
	def test_fragment_2(self):
		s = "The function of one type of parathyroid <em>cells</em> and other <em>cells</em> in the body"
		assert_that(_SearchFragmentDecorator.split_and_sanitize(s), is_(s))