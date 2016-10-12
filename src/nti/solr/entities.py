#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from nti.dataserver.interfaces import IEntity

from nti.solr.interfaces import IUsernameValue

@component.adapter(IEntity)
@interface.implementer(IUsernameValue)
class _DefaultUsernameValue(object):

	def __init__(self, context):
		self.context = context

	def value(self, context=None):
		context = self.context if context is None else context
		try:
			return context.username
		except AttributeError:
			return None
