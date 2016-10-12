#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from zope.index.interfaces import IInjection

from nti.solr.schema import SolrDatetime

from nti.schema.field import Bool
from nti.schema.field import ValidText
from nti.schema.field import ValidTextLine
from nti.schema.field import IndexedIterable

class ICoreCatalog(IInjection):
	pass

class IAttributeValue(interface.Interface):
	"""
	Adapter interface to get the [field] value from a given object
	"""

	def value():
		"""
		Return the attribute value for a given adapted object
		"""

# metadata

class IIDValue(IAttributeValue):
	"""
	Adapter interface to get the id value from a given object
	"""

class ICreatorValue(IAttributeValue):
	"""
	Adapter interface to get the creator value from a given object
	"""

class IMimeTypeValue(IAttributeValue):
	"""
	Adapter interface to get the mimeType value from a given object
	"""

class ITaggedToValue(IAttributeValue):
	"""
	Adapter interface to get the tagged-to value from a given object
	"""

class IInReplyToValue(IAttributeValue):
	"""
	Adapter interface to get the in-reply-to value from a given object
	"""

class IContainerIdValue(IAttributeValue):
	"""
	Adapter interface to get the containerId value from a given object
	"""

class ISharedWithValue(IAttributeValue):
	"""
	Adapter interface to get the sharedWith value from a given object
	"""

class ICreatedTimeValue(IAttributeValue):
	"""
	Adapter interface to get the createdTime value from a given object
	"""

class ILastModifiedValue(IAttributeValue):
	"""
	Adapter interface to get the lastModified value from a given object
	"""

class IIsDeletedObjectValue(IAttributeValue):
	"""
	Adapter interface to check if the object is deleted
	"""

class IIsTopLevelContentValue(IAttributeValue):
	"""
	Adapter interface to get the isTopLevelContent value from a given object
	"""

class IMetadataCatalog(ICoreCatalog):

	creator = ValidTextLine(title='The creator', required=False)
	creator.setTaggedValue('__solr_stored__', True)
	creator.setTaggedValue('__solr_indexed__', True)
	creator.setTaggedValue('__solr_value_interface__', ICreatorValue)

	mimeType = ValidTextLine(title='The mime type', required=False)
	mimeType.setTaggedValue('__solr_stored__', True)
	mimeType.setTaggedValue('__solr_indexed__', True)
	mimeType.setTaggedValue('__solr_value_interface__', IMimeTypeValue)

	taggedTo = IndexedIterable(title='The entities identifiers',
							   required=False,
							   value_type=ValidTextLine(title="The entiy identifier"),
							   min_length=0)
	taggedTo.setTaggedValue('__solr_stored__', True)
	taggedTo.setTaggedValue('__solr_indexed__', True)
	taggedTo.setTaggedValue('__solr_value_interface__', ITaggedToValue)
	
	inReplyTo = ValidTextLine(title='The replied to NTIID', required=False)
	inReplyTo.setTaggedValue('__solr_stored__', True)
	inReplyTo.setTaggedValue('__solr_indexed__', True)
	inReplyTo.setTaggedValue('__solr_value_interface__', IInReplyToValue)

	containerId = ValidTextLine(title='The container NTIID', required=False)
	containerId.setTaggedValue('__solr_stored__', True)
	containerId.setTaggedValue('__solr_indexed__', True)
	containerId.setTaggedValue('__solr_value_interface__', IContainerIdValue)

	sharedWith = IndexedIterable(title='The entities shared with',
							    required=False,
							    value_type=ValidTextLine(title="The entiy"),
							    min_length=0)
	sharedWith.setTaggedValue('__solr_stored__', True)
	sharedWith.setTaggedValue('__solr_indexed__', True)
	sharedWith.setTaggedValue('__solr_value_interface__', ISharedWithValue)

	createdTime = SolrDatetime(title='The %Y-%m-%dT%H:%M:%SZ created date', required=False)
	createdTime.setTaggedValue('__solr_stored__', False)
	createdTime.setTaggedValue('__solr_indexed__', True)
	createdTime.setTaggedValue('__solr_value_interface__', ICreatedTimeValue)

	lastModified = SolrDatetime(title='The %Y-%m-%dT%H:%M:%SZ last modified date', required=False)
	lastModified.setTaggedValue('__solr_stored__', False)
	lastModified.setTaggedValue('__solr_indexed__', True)
	lastModified.setTaggedValue('__solr_value_interface__', ILastModifiedValue)

	isDeletedObject = Bool(title='Is deleted object flag', required=False)
	isDeletedObject.setTaggedValue('__solr_stored__', False)
	isDeletedObject.setTaggedValue('__solr_indexed__', True)
	isDeletedObject.setTaggedValue('__solr_value_interface__', IIsDeletedObjectValue)

	isTopLevelContent = Bool(title='Is top level object flag', required=False)
	isTopLevelContent.setTaggedValue('__solr_stored__', False)
	isTopLevelContent.setTaggedValue('__solr_indexed__', True)
	isTopLevelContent.setTaggedValue('__solr_value_interface__', IIsTopLevelContentValue)

# misc

class IContentValue(IAttributeValue):
	"""
	Adapter interface to get the content value from a given object
	"""

class IKeywordsValue(IAttributeValue):
	"""
	Adapter interface to get the keywords value from a given object
	"""

# transcripts

class ITranscriptCatalog(IMetadataCatalog):

	context_en = ValidText(title='Text to index', required=False)
	context_en.setTaggedValue('__solr_stored__', False)
	context_en.setTaggedValue('__solr_indexed__', True)
	context_en.setTaggedValue('__solr_value_interface__', IContentValue)
	
	keywords = IndexedIterable(title='The keywords',
							   required=False,
							   value_type=ValidTextLine(title="The keyword"),
							   min_length=0)
	keywords.setTaggedValue('__solr_stored__', True)
	keywords.setTaggedValue('__solr_indexed__', True)
	keywords.setTaggedValue('__solr_value_interface__', IKeywordsValue)

# content units

class IContentPackageValue(IAttributeValue):
	"""
	Adapter interface to get the content pacakge ntiid value from a given object
	"""
