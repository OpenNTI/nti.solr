#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

class IAttributeValue(interface.Interface):
	"""
	Adapter interface to get the [field] value from a given object
	"""

	def value():
		"""
		Return the attribute value for a given adapted object
		"""

class ICreatorValue(IAttributeValue):
	"""
	Adapter interface to get the creator value from a given object
	"""

class IIDValue(IAttributeValue):
	"""
	Adapter interface to get the id value from a given object
	"""

class IMimeTypeValue(IAttributeValue):
	"""
	Adapter interface to get the mimeType value from a given object
	"""
