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

def tagField(field, stored=True, adapter=None, multiValued=False, indexed=True, type_=None):
	field.setTaggedValue('__solr_stored__', stored)
	field.setTaggedValue('__solr_indexed__', indexed)
	field.setTaggedValue('__solr_multiValued__', multiValued)
	field.setTaggedValue('__solr_value_interface__', adapter)
	if type_ is not None:
		field.setTaggedValue('__solr_type__', type_)

class IMetadataCatalog(ICoreCatalog):

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

tagField(IMetadataCatalog['creator'], True, ICreatorValue)
tagField(IMetadataCatalog['mimeType'], True, IMimeTypeValue)
tagField(IMetadataCatalog['inReplyTo'], True, IInReplyToValue)
tagField(IMetadataCatalog['containerId'], True, IContainerIdValue)
tagField(IMetadataCatalog['taggedTo'], True, ITaggedToValue, True)
tagField(IMetadataCatalog['createdTime'], False, ICreatedTimeValue)
tagField(IMetadataCatalog['lastModified'], False, ILastModifiedValue)
tagField(IMetadataCatalog['sharedWith'], True, ISharedWithValue, True)
tagField(IMetadataCatalog['isDeletedObject'], False, IIsDeletedObjectValue)
tagField(IMetadataCatalog['isTopLevelContent'], False, IIsTopLevelContentValue)

# misc

class IContentValue(IAttributeValue):
	"""
	Adapter interface to get the content value from a given object
	"""

class IKeywordsValue(IAttributeValue):
	"""
	Adapter interface to get the keywords value from a given object
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

class IEntitiesCatalog(IMetadataCatalog):

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

tagField(IEntitiesCatalog['email'], True, IEmailValue)
tagField(IEntitiesCatalog['alias'], True, IAliasValue)
tagField(IEntitiesCatalog['realname'], True, IRealnameValue)
tagField(IEntitiesCatalog['username'], True, IUsernameValue, True)
tagField(IEntitiesCatalog['social_url'], True, ISocialURLValue, True)
tagField(IEntitiesCatalog['education_school'], True, IEducationSchoolValue, True)
tagField(IEntitiesCatalog['education_degree'], True, IEducationDegreeValue, True)
tagField(IEntitiesCatalog['education_description'], True, IEducationDescriptionValue, True)
tagField(IEntitiesCatalog['professional_title'], True, IProfessionalTitleValue, True)
tagField(IEntitiesCatalog['professional_company'], True, IProfessionalCompanyValue, True)
tagField(IEntitiesCatalog['professional_description'], True, IProfessionalDescriptionValue, True)

# 	<!-- Each prof/educational entry may have multiple values for these fields -->
# 	
# 	<field name="education_school" type="strings" indexed="true" required="true" stored="true"/>
# 	<field name="education_desc" type="strings" indexed="true" required="true" stored="true"/>
# 	<field name="education_degree" type="strings" indexed="true" required="true" stored="true"/>
# 	<field name="social_urls" type="strings" indexed="true" required="true" stored="true"/>

# transcripts

class IMediaNTIIDValue(IAttributeValue):
	"""
	Adapter interface to get the media (video/audio) NTIID associated with a transcript object
	"""

class ITranscriptCatalog(IMetadataCatalog):

	context_en = ValidText(title='Text to index', required=False)
	
	media = ValidText(title='The media ntiid', required=False)

	keywords = IndexedIterable(title='The keywords',
							   required=False,
							   value_type=ValidTextLine(title="The keyword"),
							   min_length=0)

tagField(ITranscriptCatalog['media'], True, IMediaNTIIDValue)
tagField(ITranscriptCatalog['context_en'], True, IContentValue)
tagField(ITranscriptCatalog['keywords'], False, IKeywordsValue, True, 'text_lower')

# content units

class IContentPackageValue(IAttributeValue):
	"""
	Adapter interface to get the content pacakge ntiid value from a given object
	"""

class IContentUnitCatalog(IMetadataCatalog):

	ntiid = ValidTextLine(title='Content unit ntiid', required=False)

	package = ValidTextLine(title='Content package ntiid', required=False)

	context_en = ValidText(title='Text to index', required=False)

	keywords = IndexedIterable(title='The keywords',
							   required=False,
							   value_type=ValidTextLine(title="The keyword"),
							   min_length=0)

tagField(IContentUnitCatalog['ntiid'], True, INTIIDValue)
tagField(IContentUnitCatalog['context_en'], True, IContentValue)
tagField(IContentUnitCatalog['package'], True, IContentPackageValue)
tagField(IContentUnitCatalog['keywords'], False, IKeywordsValue, True, 'text_lower')
