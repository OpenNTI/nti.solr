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

from nti.contentlibrary.interfaces import IContentUnit
from nti.contentlibrary.interfaces import IContentPackage

from nti.solr.interfaces import IContentPackageValue

from nti.traversal.traversal import find_interface

@component.adapter(IContentUnit)
@interface.implementer(IContentPackageValue)
class _DefaultContentPackageValue(object):

	def __init__(self, context):
		self.context = context

	def value(self, context=None):
		context = self.context if context is None else context
		package = find_interface(context, IContentPackage, strict=False)
		try:
			return package.ntiid
		except AttributeError:
			return None
