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

# metadata 

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

class ICreatedTimeValue(IAttributeValue):
	"""
	Adapter interface to get the createdTime value from a given object
	"""

class ILastModifiedValue(IAttributeValue):
	"""
	Adapter interface to get the lastModified value from a given object
	"""

class IContainerIdValue(IAttributeValue):
	"""
	Adapter interface to get the containerId value from a given object
	"""

class ISharedWithValue(IAttributeValue):
	"""
	Adapter interface to get the sharedWith value from a given object
	"""

class ITaggedToValue(IAttributeValue):
	"""
	Adapter interface to get the tagged-to value from a given object
	"""

class IIsTopLevelContentValue(IAttributeValue):
	"""
	Adapter interface to get the isTopLevelContent value from a given object
	"""

class IIsDeletedObjectValue(IAttributeValue):
	"""
	Adapter interface to check if the object is deleted
	"""
	
# content units

class IContentPackageValue(IAttributeValue):
	"""
	Adapter interface to get the content pacakge ntiid value from a given object
	"""

# misc

class IContentValue(IAttributeValue):
	"""
	Adapter interface to get the content value from a given object
	"""
	
class IKeywordsValue(IAttributeValue):
	"""
	Adapter interface to get the keywords value from a given object
	"""

# core catalog

class ICoreCatalog(interface.Interface):
	pass
