#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six

from zope import component
from zope import interface

from nti.common.string import to_unicode

from nti.dataserver.interfaces import IEntity

from nti.dataserver.users.interfaces import IUserProfile 
from nti.dataserver.users.interfaces import IAboutProfile 
from nti.dataserver.users.interfaces import IFriendlyNamed
from nti.dataserver.users.interfaces import IEducationProfile
from nti.dataserver.users.interfaces import ISocialMediaProfile
from nti.dataserver.users.interfaces import IProfessionalProfile

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.solr import NTI_CATALOG
from nti.solr import ENTITIES_CATALOG

from nti.solr.catalog import CoreCatalog

from nti.solr.interfaces import IAboutValue
from nti.solr.interfaces import IAliasValue
from nti.solr.interfaces import IEmailValue
from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import IRealnameValue
from nti.solr.interfaces import IUsernameValue
from nti.solr.interfaces import IEntityDocument 
from nti.solr.interfaces import ISocialURLValue
from nti.solr.interfaces import IEducationDegreeValue
from nti.solr.interfaces import IEducationSchoolValue
from nti.solr.interfaces import IProfessionalTitleValue
from nti.solr.interfaces import IProfessionalCompanyValue
from nti.solr.interfaces import IEducationDescriptionValue
from nti.solr.interfaces import IProfessionalDescriptionValue

from nti.solr.metadata import MetadataDocument

from nti.solr.utils import document_creator
from nti.solr.utils import resolve_content_parts

class _BasicAttributeValue(object):

	field = None
	interface = None

	def __init__(self, context=None):
		self.context = context

	def value(self, context=None):
		context = self.context if context is None else context
		profile = self.interface(context, None)
		result = getattr(profile, self.field, None)
		if isinstance(result, six.string_types):
			result = to_unicode(result)
		return result

@component.adapter(IEntity)
@interface.implementer(IUsernameValue)
class _DefaultUsernameValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		result = getattr(context, 'username', None)
		return (to_unicode(result),) if result else ()

@component.adapter(IEntity)
@interface.implementer(IEmailValue)
class _DefaultEmailValue(_BasicAttributeValue):
	field = 'email'
	interface = IUserProfile

	def value(self, context=None):
		result = _BasicAttributeValue.value(self, context)
		return result.lower() if result else None

@component.adapter(IEntity)
@interface.implementer(IAliasValue)
class _DefaultAliasValue(_BasicAttributeValue):
	field = 'alias'
	interface = IFriendlyNamed
	
@component.adapter(IEntity)
@interface.implementer(IRealnameValue)
class _DefaultRealnameValue(_BasicAttributeValue):
	field = 'realname'
	interface = IFriendlyNamed

@component.adapter(IEntity)
@interface.implementer(IProfessionalTitleValue)
class _DefaultProfessionalTitleValue(_BasicAttributeValue):

	field = 'positions'
	interface = IProfessionalProfile

	def value(self, context=None):
		source = _BasicAttributeValue.value(self, context) or ()
		return tuple(to_unicode(x.title) for x in source if x.title) if source else ()

@component.adapter(IEntity)
@interface.implementer(IProfessionalCompanyValue)
class _DefaultProfessionalCompanyValue(_DefaultProfessionalTitleValue):
	
	def value(self, context=None):
		source = _BasicAttributeValue.value(self, context) or ()
		return tuple(to_unicode(x.companyName) for x in source if x.companyName) if source else ()

@component.adapter(IEntity)
@interface.implementer(IProfessionalDescriptionValue)
class _DefaultProfessionalDescriptionValue(_DefaultProfessionalTitleValue):

	def value(self, context=None):
		source = _BasicAttributeValue.value(self, context) or ()
		return tuple(to_unicode(x.description) for x in source if x.description) if source else ()

@component.adapter(IEntity)
@interface.implementer(IEducationDegreeValue)
class _DefaultEducationDegreeValue(_BasicAttributeValue):

	field = 'education'
	interface = IEducationProfile

	def value(self, context=None):
		source = _BasicAttributeValue.value(self, context) or ()
		return tuple(to_unicode(x.degree) for x in source if x.degree) if source else ()

@component.adapter(IEntity)
@interface.implementer(IEducationSchoolValue)
class _DefaultEducationSchoolValue(_DefaultEducationDegreeValue):
	
	def value(self, context=None):
		source = _BasicAttributeValue.value(self, context) or ()
		return tuple(to_unicode(x.school) for x in source if x.school) if source else ()

@component.adapter(IEntity)
@interface.implementer(IEducationDescriptionValue)
class _DefaultEducationDescriptionValue(_DefaultEducationDegreeValue):

	def value(self, context=None):
		source = _BasicAttributeValue.value(self, context) or ()
		return tuple(to_unicode(x.description) for x in source) if source else ()

@component.adapter(IEntity)
@interface.implementer(ISocialURLValue)
class _DefaultSocialURLValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		profile = ISocialMediaProfile(context, None)
		if profile is not None:
			result = {profile.twitter, profile.facebook, 
					  profile.googlePlus, profile.linkedIn}
			return tuple(to_unicode(x.lower()) for x in result if x)
		return ()

@component.adapter(IEntity)
@interface.implementer(IAboutValue)
class _DefaultAboutValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		profile = IAboutProfile(context, None)
		if profile is not None:
			return resolve_content_parts(profile.about)
		return None

@interface.implementer(IEntityDocument)
class EntityDocument(MetadataDocument):
	createDirectFieldProperties(IEntityDocument)

	mimeType = mime_type = u'application/vnd.nextthought.solr.entitydocument'
		
@component.adapter(IEntity)
@interface.implementer(IEntityDocument)
def _EntityDocumentCreator(obj, factory=EntityDocument):
	return document_creator(obj, factory=factory, provided=IEntityDocument)

@component.adapter(IEntity)
@interface.implementer(ICoreCatalog)
def _entity_to_catalog(obj):
	return component.getUtility(ICoreCatalog, name=ENTITIES_CATALOG)

class EntitiesCatalog(CoreCatalog):

	document_interface = IEntityDocument
	
	def __init__(self, name=NTI_CATALOG, client=None):
		CoreCatalog.__init__(self, name=name, client=client)
