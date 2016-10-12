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

from nti.dataserver.users.interfaces import IUserProfile, IFriendlyNamed

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
		return getattr(context, 'username', None)

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
