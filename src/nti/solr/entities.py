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

from nti.dataserver.users.interfaces import IUserProfile
from nti.dataserver.users.interfaces import IFriendlyNamed
from nti.dataserver.users.interfaces import IEducationProfile
from nti.dataserver.users.interfaces import ISocialMediaProfile
from nti.dataserver.users.interfaces import IProfessionalProfile

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.solr.interfaces import IAliasValue, IEntityDocument
from nti.solr.interfaces import IEmailValue
from nti.solr.interfaces import IRealnameValue
from nti.solr.interfaces import IUsernameValue
from nti.solr.interfaces import ISocialURLValue
from nti.solr.interfaces import IEducationDegreeValue
from nti.solr.interfaces import IEducationSchoolValue
from nti.solr.interfaces import IProfessionalTitleValue
from nti.solr.interfaces import IProfessionalCompanyValue
from nti.solr.interfaces import IEducationDescriptionValue
from nti.solr.interfaces import IProfessionalDescriptionValue

from nti.solr.metadata import MetadataDocument

from nti.solr.utils import document_creator

class _BasicAttributeValue(object):

	field = None
	interface = None

	def __init__(self, context=None):
		self.context = context

	def value(self, context=None):
		context = self.context if context is None else context
		profile = self.interface(context, None)
		return getattr(profile, self.field, None)

@component.adapter(IEntity)
@interface.implementer(IUsernameValue)
class _DefaultUsernameValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		result = getattr(context, 'username', None)
		return (result,) if result else ()

@component.adapter(IEntity)
@interface.implementer(IEmailValue)
class _DefaultEmailValue(_BasicAttributeValue):
	field = 'email'
	interface = IUserProfile

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
		positions = _BasicAttributeValue.value(self, context) or ()
		return tuple(x.title for x in positions) if positions else ()

@component.adapter(IEntity)
@interface.implementer(IProfessionalCompanyValue)
class _DefaultProfessionalCompanyValue(_DefaultProfessionalTitleValue):
	
	def value(self, context=None):
		positions = _BasicAttributeValue.value(self, context) or ()
		return tuple(x.companyName for x in positions) if positions else ()

@component.adapter(IEntity)
@interface.implementer(IProfessionalDescriptionValue)
class _DefaultProfessionalDescriptionValue(_DefaultProfessionalTitleValue):

	def value(self, context=None):
		positions = _BasicAttributeValue.value(self, context) or ()
		return tuple(x.description for x in positions) if positions else ()

@component.adapter(IEntity)
@interface.implementer(IEducationDegreeValue)
class _DefaultEducationDegreeValue(_BasicAttributeValue):

	field = 'education'
	interface = IEducationProfile

	def value(self, context=None):
		education = _BasicAttributeValue.value(self, context) or ()
		return tuple(x.degree for x in education) if education else ()

@component.adapter(IEntity)
@interface.implementer(IEducationSchoolValue)
class _DefaultEducationSchoolValue(_DefaultEducationDegreeValue):
	
	def value(self, context=None):
		education = _BasicAttributeValue.value(self, context) or ()
		return tuple(x.school for x in education) if education else ()

@component.adapter(IEntity)
@interface.implementer(IEducationDescriptionValue)
class _DefaultEducationDescriptionValue(_DefaultEducationDegreeValue):

	def value(self, context=None):
		education = _BasicAttributeValue.value(self, context) or ()
		return tuple(x.description for x in education) if education else ()

@component.adapter(IEntity)
@interface.implementer(ISocialURLValue)
class _DefaultSocialURLValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		profile = ISocialMediaProfile(context, None)
		if profile is not None:
			result = {profile.twitter, profile.facebook, 
					  profile.googlePlus, profile.linkedIn}
			result.discard(u'')
			result.discard(None)
			return tuple(result)
		return ()

@interface.implementer(IEntityDocument)
class EntityDocument(MetadataDocument):
	createDirectFieldProperties(IEntityDocument)

	mimeType = mime_type = u'application/vnd.nextthought.solr.entitydocument'
		
@component.adapter(IEntity)
@interface.implementer(IEntityDocument)
def _EntityDocumentCreator(obj, factory=EntityDocument):
	return document_creator(obj, factory=factory)
