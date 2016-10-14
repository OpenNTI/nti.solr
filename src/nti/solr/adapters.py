#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from nti.common.string import to_unicode

@component.adapter(basestring)
class _StringValue(object):

	def __init__(self, context=None):
		self.context = context

	def value(self, context=None):
		context = context if context else self.context
		return to_unicode(context) if context else None
