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

from zope.interface.interfaces import ObjectEvent
from zope.interface.interfaces import IObjectEvent

from nti.solr.schema import SolrDatetime

from nti.schema.field import Bool
from nti.schema.field import ValidText
from nti.schema.field import ValidTextLine
from nti.schema.field import IndexedIterable

class IAttributeValue(interface.Interface):
	"""
	Adapter interface to get the [field] value from a given object
	"""

	def value():
		"""
		Return the attribute value for a given adapted object
		"""

class IIDValue(IAttributeValue):
	"""
	Adapter interface to get the id value from a given object
	"""

class IStringValue(IAttributeValue):
	"""
	Marker interface to get a 'string' value from a given object
	"""

	def lang():
		"""
		Return the lang code for a 'string' value from a given object
		"""

# metadata

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

def tagField(field, stored=True, adapter=None, multiValued=False, indexed=True, type_=None):
	field.setTaggedValue('__solr_stored__', stored)
	field.setTaggedValue('__solr_indexed__', indexed)
	field.setTaggedValue('__solr_multiValued__', multiValued)
	field.setTaggedValue('__solr_value_interface__', adapter)
	if type_ is not None:
		field.setTaggedValue('__solr_type__', type_)

class ICoreDocument(interface.Interface):
	id = ValidTextLine(title='The id', required=True)
tagField(ICoreDocument['id'], True, IIDValue)

class IMetadataDocument(ICoreDocument):

	creator = ValidTextLine(title='The creator', required=False)

	mimeType = ValidTextLine(title='The mime type', required=False)

	taggedTo = IndexedIterable(title='The entities identifiers',
							   required=False,
							   value_type=ValidTextLine(title="The entiy identifier"),
							   min_length=0)

	inReplyTo = ValidTextLine(title='The replied to NTIID', required=False)

	containerId = ValidTextLine(title='The container NTIID', required=False)

	sharedWith = IndexedIterable(title='The entities shared with',
								required=False,
								value_type=ValidTextLine(title="The entiy"),
								min_length=0)

	createdTime = SolrDatetime(title='The created date', required=False)

	lastModified = SolrDatetime(title='The last modified date', required=False)

	isDeletedObject = Bool(title='Is deleted object flag', required=False)

	isTopLevelContent = Bool(title='Is top level object flag', required=False)

tagField(IMetadataDocument['creator'], True, ICreatorValue)
tagField(IMetadataDocument['mimeType'], True, IMimeTypeValue)
tagField(IMetadataDocument['inReplyTo'], True, IInReplyToValue)
tagField(IMetadataDocument['containerId'], True, IContainerIdValue)
tagField(IMetadataDocument['taggedTo'], True, ITaggedToValue, True)
tagField(IMetadataDocument['createdTime'], False, ICreatedTimeValue)
tagField(IMetadataDocument['lastModified'], False, ILastModifiedValue)
tagField(IMetadataDocument['sharedWith'], True, ISharedWithValue, True)
tagField(IMetadataDocument['isDeletedObject'], False, IIsDeletedObjectValue)
tagField(IMetadataDocument['isTopLevelContent'], False, IIsTopLevelContentValue)

# misc

class IContentValue(IStringValue):
	"""
	Adapter interface to get the content value from a given object
	"""

class IKeywordsValue(IAttributeValue):
	"""
	Adapter interface to get the keywords value from a given object
	"""

	def lang():
		"""
		Return the lang code for a keywords value from a given object
		"""

class INTIIDValue(IAttributeValue):
	"""
	Adapter interface to get the ntiid value from a given object
	"""

# entities

class IUsernameValue(IAttributeValue):
	"""
	Adapter interface to get the username value from a given object
	"""

class IAliasValue(IAttributeValue):
	"""
	Adapter interface to get the alias value from a given object
	"""

class IRealnameValue(IAttributeValue):
	"""
	Adapter interface to get the realname value from a given object
	"""

class IEmailValue(IAttributeValue):
	"""
	Adapter interface to get the email value from a given object
	"""

class IProfessionalTitleValue(IAttributeValue):
	"""
	Adapter interface to get the professional titles from a given entity object
	"""

class IProfessionalCompanyValue(IAttributeValue):
	"""
	Adapter interface to get the professional companies from a given entity object
	"""

class IProfessionalDescriptionValue(IAttributeValue):
	"""
	Adapter interface to get the professional descriptions from a given entity object
	"""

class IEducationSchoolValue(IAttributeValue):
	"""
	Adapter interface to get the education schools from a given entity object
	"""

class IEducationDegreeValue(IAttributeValue):
	"""
	Adapter interface to get the education degrees from a given entity object
	"""

class IEducationDescriptionValue(IAttributeValue):
	"""
	Adapter interface to get the education descriptions from a given entity object
	"""

class ISocialURLValue(IAttributeValue):
	"""
	Adapter interface to get the social URLs from a given entity object
	"""

class IEntityDocument(IMetadataDocument):

	username = IndexedIterable(title='The username identifiers',
							   required=False,
							   value_type=ValidTextLine(title="The username"),
							   min_length=1)

	alias = ValidTextLine(title='The alias', required=False)

	email = ValidTextLine(title='The username', required=False)

	realname = ValidTextLine(title='The realname', required=False)

	education_school = IndexedIterable(title='The school names',
							   		   required=False,
							   		   value_type=ValidTextLine(title="The school name"),
							   		   min_length=0)

	education_degree = IndexedIterable(title='The school degrees',
							   		   required=False,
							   		   value_type=ValidTextLine(title="The school degree"),
							   		   min_length=0)

	education_description = IndexedIterable(title='The education descriptions',
							   			    required=False,
							   			    value_type=ValidTextLine(title="The description"),
							   			    min_length=0)

	professional_description = IndexedIterable(title='The professional company descriptions',
							   			   	  required=False,
							   			   	  value_type=ValidTextLine(title="The description"),
							   			      min_length=0)


	professional_title = IndexedIterable(title='The company names',
							   			 required=False,
							   			 value_type=ValidTextLine(title="The company name"),
							   			 min_length=0)

	professional_company = IndexedIterable(title='The company names',
							   			   required=False,
							   			   value_type=ValidTextLine(title="The company name"),
							   			   min_length=0)

	professional_description = IndexedIterable(title='The professional company descriptions',
							   			   	  required=False,
							   			   	  value_type=ValidTextLine(title="The description"),
							   			      min_length=0)

	social_url = IndexedIterable(title='The social URLS',
							   	 required=False,
							   	 value_type=ValidTextLine(title="The url"),
							   	 min_length=0)

tagField(IEntityDocument['email'], True, IEmailValue)
tagField(IEntityDocument['alias'], True, IAliasValue)
tagField(IEntityDocument['realname'], True, IRealnameValue)
tagField(IEntityDocument['username'], True, IUsernameValue, True)
tagField(IEntityDocument['social_url'], True, ISocialURLValue, True)
tagField(IEntityDocument['education_school'], True, IEducationSchoolValue, True)
tagField(IEntityDocument['education_degree'], True, IEducationDegreeValue, True)
tagField(IEntityDocument['education_description'], True, IEducationDescriptionValue, True)
tagField(IEntityDocument['professional_title'], True, IProfessionalTitleValue, True)
tagField(IEntityDocument['professional_company'], True, IProfessionalCompanyValue, True)
tagField(IEntityDocument['professional_description'], True, IProfessionalDescriptionValue, True)

class IMediaNTIIDValue(IAttributeValue):
	"""
	Adapter interface to get the media (video/audio) NTIID associated with a transcript object
	"""

class ITranscriptDocument(IMetadataDocument):

	content_en = ValidText(title='Text to index', required=False)

	media = ValidText(title='The media ntiid', required=False)

	keywords_en = IndexedIterable(title='The keywords',
							   	  required=False,
							   	  value_type=ValidTextLine(title="The keyword"),
							   	  min_length=0)

tagField(ITranscriptDocument['media'], True, IMediaNTIIDValue)
tagField(ITranscriptDocument['content_en'], True, IContentValue)
tagField(ITranscriptDocument['keywords_en'], False, IKeywordsValue, True, 'text_lower')

# content units

class ITitleValue(IStringValue):
	"""
	Adapter interface to get the title value from a given object
	"""

class IContentPackageValue(IAttributeValue):
	"""
	Adapter interface to get the content pacakge ntiid value from a given object
	"""

class IContentUnitDocument(IMetadataDocument):

	ntiid = ValidTextLine(title='Content unit ntiid', required=False)

	package = ValidTextLine(title='Content package ntiid', required=False)

	title_en = ValidTextLine(title='Title to index', required=False)

	content_en = ValidText(title='Text to index', required=False)

	keywords_en = IndexedIterable(title='The keywords',
							  	  required=False,
							  	  value_type=ValidTextLine(title="The keyword"),
							   	  min_length=0)

tagField(IContentUnitDocument['ntiid'], True, INTIIDValue)
tagField(IContentUnitDocument['title_en'], True, ITitleValue)
tagField(IContentUnitDocument['content_en'], True, IContentValue)
tagField(IContentUnitDocument['package'], True, IContentPackageValue)
tagField(IContentUnitDocument['keywords_en'], False, IKeywordsValue, True, 'text_lower')

# user data

class ITagsValue(IAttributeValue):
	"""
	Adapter interface to get the tag values from a given object
	"""

class IUserDataDocument(IMetadataDocument):

	content_en = ValidText(title='Text to index', required=False)

	title_en = ValidTextLine(title='Title to index', required=False)

	tags = IndexedIterable(title='The tags',
						   required=False,
						   value_type=ValidTextLine(title="The tag"),
						   min_length=0)

	keywords_en = IndexedIterable(title='The keywords',
							  	  required=False,
							  	  value_type=ValidTextLine(title="The keyword"),
							   	  min_length=0)

tagField(IUserDataDocument['tags'], True, ITagsValue)
tagField(IUserDataDocument['title_en'], True, ITitleValue)
tagField(IUserDataDocument['content_en'], True, IContentValue)
tagField(IUserDataDocument['keywords_en'], False, IKeywordsValue, True, 'text_lower')

class IAssetDocument(IMetadataDocument):

	ntiid = ValidTextLine(title='Asset ntiid', required=False)

	title_en = ValidTextLine(title='Title to index', required=False)

	content_en = ValidText(title='Text to index', required=False)

	keywords_en = IndexedIterable(title='The keywords',
							  	  required=False,
							  	  value_type=ValidTextLine(title="The keyword"),
							   	  min_length=0)

tagField(IAssetDocument['ntiid'], True, INTIIDValue)
tagField(IAssetDocument['title_en'], True, ITitleValue)
tagField(IAssetDocument['content_en'], True, IContentValue)
tagField(IAssetDocument['keywords_en'], False, IKeywordsValue, True, 'text_lower')

class ICoreCatalog(IInjection):

	name = ValidTextLine(title="Core name", required=True)

	def add(value):
		"""
		Add a document to the index.

		@param value: the object to be indexed
		"""

	def remove(value):
		"""
		Remove a document from the index

		@param value: The object/id to remove
		"""

class IObjectIndexedEvent(IObjectEvent):
	doc_id = ValidTextLine(title='Document id')

@interface.implementer(IObjectIndexedEvent)
class ObjectIndexedEvent(ObjectEvent):
	
	def __init__(self, obj, doc_id=None):
		ObjectEvent.__init__(self, obj)
		self.doc_id = doc_id

class IObjectUnindexedEvent(IObjectEvent):
	doc_id = ValidTextLine(title='Document id')

@interface.implementer(IObjectUnindexedEvent)
class ObjectUnindexedEvent(ObjectEvent):

	def __init__(self, obj, doc_id=None):
		ObjectEvent.__init__(self, obj)
		self.doc_id = doc_id

# registration

class ISOLRQueueFactory(interface.Interface):
	"""
	A factory for SOLR processing queues.
	"""

class ISOLR(interface.Interface):
	URL = ValidTextLine(title="LDAP URL", required=True)
	Timeout = ValidTextLine(title="Timeout", required=False)
