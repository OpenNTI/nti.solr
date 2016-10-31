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
from zope.index.interfaces import IIndexSearch

from zope.interface.interfaces import ObjectEvent
from zope.interface.interfaces import IObjectEvent

from nti.solr.schema import SolrDatetime

from nti.schema.field import Bool
from nti.schema.field import IndexedIterable
from nti.schema.field import Text as ValidText
from nti.schema.field import TextLine as ValidTextLine

class ITextField(interface.Interface):
	"""
	Marker interface for text fields
	"""

class IDateField(interface.Interface):
	"""
	Marker interface for date fields
	"""

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

class ISiteValue(IAttributeValue):
	"""
	Adapter interface to get the site value from a given object
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
	Adapter interface to get the containerId values from a given object
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

def tagField(field, stored=True, adapter=None, multiValued=False, indexed=True,
			 type_=None, boost=None, provided=None):
	field.setTaggedValue('__solr_stored__', stored)
	field.setTaggedValue('__solr_indexed__', indexed)
	field.setTaggedValue('__solr_multiValued__', multiValued)
	field.setTaggedValue('__solr_value_interface__', adapter)
	if type_ is not None:
		field.setTaggedValue('__solr_type__', type_)
	if boost is not None:
		field.setTaggedValue('__solr_boost__', boost)
	if provided is not None:
		interface.alsoProvides(field, provided)

class ICoreDocument(interface.Interface):
	id = ValidTextLine(title='The id', required=True)
tagField(ICoreDocument['id'], True, IIDValue)

class IMetadataDocument(ICoreDocument):
	site = ValidTextLine(title='The site', required=False)

	creator = ValidTextLine(title='The creator', required=False)

	mimeType = ValidTextLine(title='The mime type', required=False)

	taggedTo = IndexedIterable(title='The entities identifiers',
							   required=False,
							   value_type=ValidTextLine(title="The entiy identifier"),
							   min_length=0)

	inReplyTo = ValidTextLine(title='The replied to NTIID', required=False)

	containerId = IndexedIterable(title='The container identifiers',
							   	  required=False,
							      value_type=ValidTextLine(title="The container identifier"),
							      min_length=0)

	sharedWith = IndexedIterable(title='The entities shared with',
								required=False,
								value_type=ValidTextLine(title="The entiy"),
								min_length=0)

	createdTime = SolrDatetime(title='The created date', required=False)

	lastModified = SolrDatetime(title='The last modified date', required=False)

	isDeletedObject = Bool(title='Is deleted object flag', required=False)

	isTopLevelContent = Bool(title='Is top level object flag', required=False)

tagField(IMetadataDocument['site'], False, ISiteValue)
tagField(IMetadataDocument['creator'], True, ICreatorValue)
tagField(IMetadataDocument['mimeType'], True, IMimeTypeValue)
tagField(IMetadataDocument['inReplyTo'], False, IInReplyToValue)
tagField(IMetadataDocument['isDeletedObject'], False, IIsDeletedObjectValue)
tagField(IMetadataDocument['isTopLevelContent'], False, IIsTopLevelContentValue)
tagField(IMetadataDocument['taggedTo'], True, ITaggedToValue, multiValued=True)
tagField(IMetadataDocument['sharedWith'], True, ISharedWithValue, multiValued=True)
tagField(IMetadataDocument['containerId'], False, IContainerIdValue, multiValued=True)
tagField(IMetadataDocument['createdTime'], False, ICreatedTimeValue, provided=IDateField)
tagField(IMetadataDocument['lastModified'], False, ILastModifiedValue, provided=IDateField)
# misc

class IContentValue(IStringValue):
	"""
	Adapter interface to get the content value from a given object
	"""

class IKeywordsValue(IStringValue):
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

class IAboutValue(IStringValue):
	"""
	Adapter interface to get the about value from a given entity object
	"""

class IEntityDocument(IMetadataDocument):

	username = IndexedIterable(title='The username identifiers',
							   required=False,
							   value_type=ValidTextLine(title="The username"),
							   min_length=1)

	alias = ValidTextLine(title='The alias', required=False)

	email = ValidTextLine(title='The username', required=False)

	realname = ValidTextLine(title='The realname', required=False)

	about_en = ValidText(title='The about statement', required=False)

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
tagField(IEntityDocument['alias'], True, IAliasValue, type_='text_lower')
tagField(IEntityDocument['realname'], True, IRealnameValue, type_='text_lower')
tagField(IEntityDocument['username'], True, IUsernameValue, True)
tagField(IEntityDocument['social_url'], True, ISocialURLValue, True)
tagField(IEntityDocument['about_en'], False, IAboutValue, provided=ITextField)
tagField(IEntityDocument['education_school'], True, IEducationSchoolValue, True, type_='text_lower', provided=ITextField)
tagField(IEntityDocument['education_degree'], True, IEducationDegreeValue, True, type_='text_lower', provided=ITextField)
tagField(IEntityDocument['education_description'], True, IEducationDescriptionValue, True, type_='text_lower', provided=ITextField)
tagField(IEntityDocument['professional_title'], True, IProfessionalTitleValue, True, type_='text_lower', provided=ITextField)
tagField(IEntityDocument['professional_company'], True, IProfessionalCompanyValue, True, type_='text_lower', provided=ITextField)
tagField(IEntityDocument['professional_description'], True, IProfessionalDescriptionValue, True, type_='text_lower', provided=ITextField)

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
tagField(ITranscriptDocument['content_en'], True, IContentValue, provided=ITextField)
tagField(ITranscriptDocument['keywords_en'], False, IKeywordsValue, True, 'text_lower', provided=ITextField)

# content units

class ITitleValue(IStringValue):
	"""
	Adapter interface to get the title value from a given object
	"""

class IContentUnitDocument(IMetadataDocument):

	ntiid = ValidTextLine(title='Content unit ntiid', required=False)

	title_en = ValidTextLine(title='Title to index', required=False)

	content_en = ValidText(title='Text to index', required=False)

	keywords_en = IndexedIterable(title='The keywords',
							  	  required=False,
							  	  value_type=ValidTextLine(title="The keyword"),
							   	  min_length=0)

tagField(IContentUnitDocument['ntiid'], True, INTIIDValue)
tagField(IContentUnitDocument['title_en'], True, ITitleValue, provided=ITextField)
tagField(IContentUnitDocument['content_en'], True, IContentValue, provided=ITextField)
tagField(IContentUnitDocument['keywords_en'], False, IKeywordsValue, True, 'text_lower', provided=ITextField)

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
tagField(IUserDataDocument['title_en'], True, ITitleValue, provided=ITextField)
tagField(IUserDataDocument['content_en'], True, IContentValue, provided=ITextField)
tagField(IUserDataDocument['keywords_en'], False, IKeywordsValue, True, 'text_lower', provided=ITextField)

class IAssetDocument(IMetadataDocument):

	ntiid = ValidTextLine(title='Asset ntiid', required=False)

	title_en = ValidTextLine(title='Title to index', required=False)

	content_en = ValidText(title='Text to index', required=False)

	keywords_en = IndexedIterable(title='The keywords',
							  	  required=False,
							  	  value_type=ValidTextLine(title="The keyword"),
							   	  min_length=0)

tagField(IAssetDocument['ntiid'], True, INTIIDValue)
tagField(IAssetDocument['title_en'], True, ITitleValue, provided=ITextField)
tagField(IAssetDocument['content_en'], True, IContentValue, provided=ITextField)
tagField(IAssetDocument['keywords_en'], False, IKeywordsValue, True, 'text_lower', provided=ITextField)

class ICourseCatalogDocument(IMetadataDocument):

	ntiid = ValidTextLine(title='Course catalog ntiid', required=False)

	title_en = ValidTextLine(title='Title to index', required=False)

	content_en = ValidText(title='Text to index', required=False)

	keywords_en = IndexedIterable(title='The keywords',
							  	  required=False,
							  	  value_type=ValidTextLine(title="The keyword"),
							   	  min_length=0)

tagField(ICourseCatalogDocument['ntiid'], True, INTIIDValue)
tagField(ICourseCatalogDocument['title_en'], True, ITitleValue, provided=ITextField)
tagField(ICourseCatalogDocument['content_en'], True, IContentValue, provided=ITextField)
tagField(ICourseCatalogDocument['keywords_en'], False, IKeywordsValue, True, 'text_lower', provided=ITextField)

class IEvaluationDocument(IMetadataDocument):

	ntiid = ValidTextLine(title='Evaluation ntiid', required=False)

	title_en = ValidTextLine(title='Title to index', required=False)

	content_en = ValidText(title='Text to index', required=False)

	keywords_en = IndexedIterable(title='The keywords',
							  	  required=False,
							  	  value_type=ValidTextLine(title="The keyword"),
							   	  min_length=0)

tagField(IEvaluationDocument['ntiid'], True, INTIIDValue)
tagField(IEvaluationDocument['title_en'], True, ITitleValue, provided=ITextField)
tagField(IEvaluationDocument['content_en'], True, IContentValue, provided=ITextField)
tagField(IEvaluationDocument['keywords_en'], False, IKeywordsValue, True, 'text_lower', provided=ITextField)

class ICoreCatalog(IInjection, IIndexSearch):

	name = ValidTextLine(title="Core name", required=True)

	def add(value, commit=True):
		"""
		Add a document to the index.

		@param value: the object to be indexed
		@param commit: Commit operation
		"""

	def remove(value, commit=True):
		"""
		Remove a document from the index

		@param value: The object/id to remove
		@param commit: Commit operation
		"""

	def delete(uid=None, q=None, commit=True):
		"""
		Delete by the specified query or id

		@param uid: The object/id to remove
		@param q: The query to execute for deletion
		@param commit: Commit operation
		"""

class IIndexObjectEvent(IObjectEvent):
	"""
	Event to signal object must be indexed
	"""

@interface.implementer(IIndexObjectEvent)
class IndexObjectEvent(ObjectEvent):
	pass

class IUnindexObjectEvent(IObjectEvent):
	"""
	Event to signal object must be unindexed
	"""

@interface.implementer(IUnindexObjectEvent)
class UnindexObjectEvent(ObjectEvent):
	pass

class IObjectIndexedEvent(IObjectEvent):
	"""
	Event to signal an object has been indexed
	"""
	doc_id = ValidTextLine(title='Document id')

@interface.implementer(IObjectIndexedEvent)
class ObjectIndexedEvent(ObjectEvent):

	def __init__(self, obj, doc_id=None):
		ObjectEvent.__init__(self, obj)
		self.doc_id = doc_id

class IObjectUnindexedEvent(IObjectEvent):
	"""
	Event to signal an object has been unindexed
	"""
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

class ISolrResultTransformer(interface.Interface):
	"""
	An adapter interface to transform an object into
	an appropriate object to return on hits.
	"""
