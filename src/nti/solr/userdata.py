#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import itertools

from zope import component
from zope import interface

from nti.coremetadata.interfaces import IModeledContentBody

from nti.coremetadata.utils import current_principal

from nti.dataserver.authentication import effective_principals

from nti.dataserver.interfaces import IUserGeneratedData

from nti.dataserver.users import User

from nti.property.property import Lazy

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.solr import USERDATA_CATALOG

from nti.solr.catalog import CoreCatalog

from nti.solr.interfaces import ITitleValue
from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import IKeywordsValue
from nti.solr.interfaces import IUserDataDocument

from nti.solr.metadata import MetadataDocument

from nti.solr.utils import get_keywords
from nti.solr.utils import document_creator
from nti.solr.utils import resolve_content_parts

class _BasicAttributeValue(object):

	def __init__(self, context=None):
		self.context = context

@interface.implementer(ITitleValue)
@component.adapter(IUserGeneratedData)
class _DefaultUserDataTitleValue(_BasicAttributeValue):

	def lang(self, context):
		return 'en'

	def value(self, context=None):
		context = self.context if context is None else context
		return getattr(context, 'title', None)

@interface.implementer(IContentValue)
@component.adapter(IUserGeneratedData)
class _DefaultUserDataContentValue(_BasicAttributeValue):

	language = 'en'

	def lang(self, context=None):
		return self.language

	def get_content(self, context):
		if IModeledContentBody.providedBy(context):
			return resolve_content_parts(context.body)
		return None

	def value(self, context=None):
		context = self.context if context is None else context
		return self.get_content(context)

@component.adapter(IUserGeneratedData)
@interface.implementer(IKeywordsValue)
class _DefaultUserDataKeywordsValue(_BasicAttributeValue):

	language = 'en'

	def lang(self, context=None):
		return self.language

	def value(self, context=None):
		context = self.context if context is None else context
		adapted = IContentValue(context, None)
		if adapted is not None:
			self.language = adapted.lang()
			return get_keywords(adapted.value(), self.language)
		return ()

@interface.implementer(IUserDataDocument)
class UserDataDocument(MetadataDocument):
	createDirectFieldProperties(IUserDataDocument)

	mimeType = mime_type = u'application/vnd.nextthought.solr.usergenerateddatadocument'

@component.adapter(IUserGeneratedData)
@interface.implementer(IUserDataDocument)
def _UserDataDocumentCreator(obj, factory=UserDataDocument):
	return document_creator(obj, factory=factory, provided=IUserDataDocument)

@interface.implementer(ICoreCatalog)
@component.adapter(IUserGeneratedData)
def _userdata_to_catalog(obj):
	return component.getUtility(ICoreCatalog, name=USERDATA_CATALOG)

class UserDataCatalog(CoreCatalog):

	document_interface = IUserDataDocument

	def __init__(self, client=None):
		CoreCatalog.__init__(self, USERDATA_CATALOG, client)

	# principal methods

	@Lazy
	def username(self):
		try:
			return current_principal(False).id
		except AttributeError:
			return None

	@Lazy
	def entity(self):
		try:
			return User.get_entity(self.username)
		except (LookupError, TypeError):
			return None

	@Lazy
	def memberships(self):
		user = self.entity
		if user is not None:
			dynamic_memberships = getattr(user, 'usernames_of_dynamic_memberships', ())
			usernames = itertools.chain((user.username,), dynamic_memberships)
			return {x.lower() for x in usernames}
		return ()

	@Lazy
	def effective_principals(self):
		return effective_principals(self.username, everyone=False, skip_cache=True)
