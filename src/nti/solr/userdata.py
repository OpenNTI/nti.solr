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

from nti.chatserver.interfaces import IMessageInfo

from nti.coremetadata.interfaces import IModeledContentBody

from nti.dataserver.contenttypes.forums.interfaces import IHeadlineTopic

from nti.dataserver.interfaces import IUser
from nti.dataserver.interfaces import IHighlight 
from nti.dataserver.interfaces import IRedaction
from nti.dataserver.interfaces import ITaggedContent
from nti.dataserver.interfaces import ITitledContent
from nti.dataserver.interfaces import IUserGeneratedData

from nti.dataserver.users import User

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.solr import USERDATA_CATALOG

from nti.solr.interfaces import ITagsValue
from nti.solr.interfaces import ITitleValue
from nti.solr.interfaces import ICoreCatalog
from nti.solr.interfaces import IChannelValue
from nti.solr.interfaces import IContentValue
from nti.solr.interfaces import ICreatorValue
from nti.solr.interfaces import IKeywordsValue
from nti.solr.interfaces import IRecipientsValue
from nti.solr.interfaces import ISharedWithValue
from nti.solr.interfaces import IExplanationValue
from nti.solr.interfaces import IUserDataDocument
from nti.solr.interfaces import IReplacementContentValue

from nti.solr.lucene import lucene_escape

from nti.solr.metadata import MetadataCatalog
from nti.solr.metadata import MetadataDocument
from nti.solr.metadata import DefaultSharedWithValue

from nti.solr.utils import CATALOG_MIME_TYPE_MAP

from nti.solr.utils import get_keywords
from nti.solr.utils import document_creator
from nti.solr.utils import resolve_content_parts

class _BasicAttributeValue(object):

	def __init__(self, context=None, default=None):
		self.context = context

@component.adapter(ISharedWithValue)
@interface.implementer(IUserGeneratedData)
class _UserDataSharedWithValue(DefaultSharedWithValue):
	
	def value(self, context=None):
		context = self.context if context is None else context
		sharedWith = set(DefaultSharedWithValue.value(self, context) or ())
		sharedWith = sharedWith.add(ICreatorValue(context).value())
		return tuple(sharedWith)

@component.adapter(ITitledContent)
@interface.implementer(ITitleValue)
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

@component.adapter(IHighlight)
@interface.implementer(IContentValue)
class _HighlightContentValue(_DefaultUserDataContentValue):

	def get_content(self, context):
		return context.selectedText

@component.adapter(IHeadlineTopic)
@interface.implementer(ITitleValue)
class _HeadlineTopicTitleValue(_BasicAttributeValue):

	def value(self, context=None):
		return None

@component.adapter(IHeadlineTopic)
@interface.implementer(IContentValue)
class _HeadlineTopicContentValue(_DefaultUserDataContentValue):

	def value(self, context=None):
		return None

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

@component.adapter(ITaggedContent)
@interface.implementer(ITagsValue)
class _DefaultTaggsValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		return context.tags or ()

@component.adapter(IMessageInfo)
@interface.implementer(IChannelValue)
class _DefaultChannelValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		return context.channel

@component.adapter(IMessageInfo)
@interface.implementer(IRecipientsValue)
class _DefaultRecipientsValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		return tuple(x.lower() for x in context.recipients if x)

@component.adapter(IRedaction)
@interface.implementer(IExplanationValue)
class _DefaultRedactionExplanationValue(_BasicAttributeValue):

	def lang(self, context):
		return 'en'

	def value(self, context=None):
		context = self.context if context is None else context
		return context.redactionExplanation

@component.adapter(IRedaction)
@interface.implementer(IReplacementContentValue)
class _DefaultReplacementContentValue(_BasicAttributeValue):

	def lang(self, context):
		return 'en'

	def value(self, context=None):
		context = self.context if context is None else context
		return context.replacementContent

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

@interface.implementer(ICoreCatalog)
class UserDataCatalog(MetadataCatalog):

	name = USERDATA_CATALOG
	document_interface = IUserDataDocument

	# principal methods

	def get_entity(self, username):
		try:
			return User.get_entity(username)
		except (LookupError, TypeError):
			return None

	def memberships(self, username):
		user = self.get_entity(username)
		if IUser.providedBy(user):
			dynamic_memberships = user.usernames_of_dynamic_memberships or ()
			usernames = itertools.chain((user.username,), dynamic_memberships)
			return {x.lower() for x in usernames} - {'everyone'}
		return ()

	# search methods

	def _build_from_search_query(self, query, text_fields=None, return_fields=None):
		term, fq, params = MetadataCatalog._build_from_search_query(self, query,
																	text_fields,
																	return_fields)
		username = getattr(query, 'username', None)
		memberships = self.memberships(username)
		if username and 'sharedWith' not in fq and username and memberships:
			fq['sharedWith'] = "(%s)" % self._OR_.join(lucene_escape(x) for x in memberships)
		fq['isUserGeneratedData'] = "true" # always
		searchOn = getattr(query, 'searchOn', None)
		if 'mimeType' not in fq and searchOn:
			types = CATALOG_MIME_TYPE_MAP.get(self.name) # XXX: Negative list
			fq['mimeType'] = "(%s)" % self._OR_.join(lucene_escape(x) for x in searchOn if x not in types)
		return term, fq, params

	def clear(self, username=None, commit=None):
		q = ["isUserGeneratedData:true"]
		if username:
			q.append("creator:%s" % lucene_escape(username))
		q = "(%s)" % self._AND_.join(q)
		self.client.delete(q=q, commit=self.auto_commit if commit is None else bool(commit))
	reset = clear
