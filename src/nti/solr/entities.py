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
from nti.dataserver.users.interfaces import IProfessionalProfile

from nti.solr.interfaces import IAliasValue
from nti.solr.interfaces import IEmailValue
from nti.solr.interfaces import IRealnameValue
from nti.solr.interfaces import IUsernameValue

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
@interface.implementer(IUsernameValue)
class _DefaultProfessionalCompanyValue(_BasicAttributeValue):

	field = 'positions'
	interface = IProfessionalProfile
	
	def value(self, context=None):
		positions = _BasicAttributeValue.value(self, context) or ()
		return tuple(x.companyName for x in positions) if positions else ()

@component.adapter(IEntity)
@interface.implementer(IUsernameValue)
class _DefaultProfessionalDescriptionValue(_DefaultProfessionalCompanyValue):

	def value(self, context=None):
		positions = _BasicAttributeValue.value(self, context) or ()
		return tuple(x.description for x in positions) if positions else ()

@component.adapter(IEntity)
@interface.implementer(IUsernameValue)
class _DefaultProfessionalTitleValue(_DefaultProfessionalCompanyValue):

	def value(self, context=None):
		positions = _BasicAttributeValue.value(self, context) or ()
		return tuple(x.title for x in positions) if positions else ()
