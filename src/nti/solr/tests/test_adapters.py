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

from zope import interface

from nti.coremetadata.interfaces import ICreated

from nti.solr.interfaces import ICreatorValue

from nti.solr.tests import SOLRTestLayer

class TestAdpaters(unittest.TestCase):

	layer = SOLRTestLayer

	def test_creator(self):

		@interface.implementer(ICreated)
		class Created(object):
			creator = 'ichigo'

		value = ICreatorValue(Created()).value()
		assert_that(value, is_('ichigo'))
