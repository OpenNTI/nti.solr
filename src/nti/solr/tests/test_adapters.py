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

from zope.mimetype.interfaces import IContentTypeAware

from nti.coremetadata.interfaces import ICreated
from nti.coremetadata.interfaces import ICreatedTime 
from nti.coremetadata.interfaces import ILastModified 

from nti.solr.interfaces import INTIIDValue
from nti.solr.interfaces import ICreatorValue
from nti.solr.interfaces import IMimeTypeValue
from nti.solr.interfaces import IInReplyToValue
from nti.solr.interfaces import ISharedWithValue
from nti.solr.interfaces import ICreatedTimeValue
from nti.solr.interfaces import ILastModifiedValue

from nti.solr.tests import SOLRTestLayer

class TestAdpaters(unittest.TestCase):

	layer = SOLRTestLayer

	def test_creator(self):

		@interface.implementer(ICreated)
		class Created(object):
			creator = 'ichigo'

		value = ICreatorValue(Created()).value()
		assert_that(value, is_('ichigo'))

	def test_mimetype(self):

		@interface.implementer(IContentTypeAware)
		class Created(object):
			mimeType = 'text/x-python'

		value = IMimeTypeValue(Created()).value()
		assert_that(value, is_('text/x-python'))
		
	def test_ntiid(self):

		@interface.implementer(IContentTypeAware)
		class Created(object):
			ntiid = 'foo'

		value = INTIIDValue(Created()).value()
		assert_that(value, is_('foo'))

	def test_created_last_mod_times(self):

		@interface.implementer(ICreatedTime, ILastModified)
		class Created(object):
			lastModified = createdTime = 1475604175.0

		obj = Created()
		for iface in (ICreatedTimeValue, ILastModifiedValue):
			value = iface(obj).value()
			assert_that(value, is_('2016-10-04T18:02:55Z'))
			
	def test_sharedWith(self):

		class Created(object):
			sharedWith = ("ichigo", 'Aizen')

		value = ISharedWithValue(Created()).value()
		assert_that(value, is_(('ichigo', 'aizen')))
		
	def test_inReplyTo(self):

		class Created(object):
			inReplyTo = "Aizen"

		value = IInReplyToValue(Created()).value()
		assert_that(value, is_('aizen'))
