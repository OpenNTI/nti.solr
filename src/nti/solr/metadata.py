#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import re
import six
from math import ceil
from datetime import datetime

from zope import component
from zope import interface

from zope.component.hooks import getSite

from zope.intid.interfaces import IIntIds

from zope.mimetype.interfaces import IContentTypeAware

from nti.common.string import to_unicode

from nti.coremetadata.interfaces import SYSTEM_USER_NAME

from nti.coremetadata.interfaces import ICreatedTime
from nti.coremetadata.interfaces import ILastModified

from nti.dataserver.contenttypes.forums.interfaces import ICommentPost
from nti.dataserver.contenttypes.forums.interfaces import IHeadlinePost
from nti.dataserver.contenttypes.forums.interfaces import IPersonalBlogEntryPost

from nti.dataserver.interfaces import IUser
from nti.dataserver.interfaces import IDevice
from nti.dataserver.interfaces import IThreadable
from nti.dataserver.interfaces import IFriendsList
from nti.dataserver.interfaces import IModeledContent
from nti.dataserver.interfaces import IUserGeneratedData
from nti.dataserver.interfaces import IUserTaggedContent
from nti.dataserver.interfaces import IDeletedObjectPlaceholder
from nti.dataserver.interfaces import IInspectableWeakThreadable
from nti.dataserver.interfaces import IContained as INTIContained
from nti.dataserver.interfaces import IDynamicSharingTargetFriendsList

from nti.ntiids.ntiids import TYPE_OID
from nti.ntiids.ntiids import TYPE_UUID
from nti.ntiids.ntiids import TYPE_INTID
from nti.ntiids.ntiids import TYPE_MEETINGROOM
from nti.ntiids.ntiids import TYPE_NAMED_ENTITY

from nti.ntiids.ntiids import is_ntiid_of_types
from nti.ntiids.ntiids import find_object_with_ntiid

from nti.schema.field import SchemaConfigured
from nti.schema.fieldproperty import createDirectFieldProperties

from nti.site.interfaces import IHostPolicyFolder

from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import ISiteValue
from nti.solr.interfaces import INTIIDValue
from nti.solr.interfaces import ICreatorValue
from nti.solr.interfaces import IMimeTypeValue
from nti.solr.interfaces import ITaggedToValue
from nti.solr.interfaces import IInReplyToValue
from nti.solr.interfaces import ISharedWithValue
from nti.solr.interfaces import IContainerIdValue
from nti.solr.interfaces import ICreatedTimeValue
from nti.solr.interfaces import IMetadataDocument
from nti.solr.interfaces import ILastModifiedValue
from nti.solr.interfaces import IIsDeletedObjectValue
from nti.solr.interfaces import IIsTopLevelContentValue
from nti.solr.interfaces import IIsUserGeneratedDataValue

from nti.solr.schema import SolrDatetime

from nti.solr.utils import document_creator

from nti.traversal.traversal import find_interface

ZERO_DATETIME = datetime.utcfromtimestamp(0)

class _BasicAttributeValue(object):

	def __init__(self, context=None):
		self.context = context

@interface.implementer(ISiteValue)
class _DefaultSiteValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		folder = find_interface(context, IHostPolicyFolder, strict=False)
		return folder.__name__ if folder is not None else getSite().__name__

@interface.implementer(ICreatorValue)
class _DefaultCreatorValue(_BasicAttributeValue):

	def _get_creator(self, context, name='creator'):
		try:
			creator = getattr(context, name, None)
			creator = getattr(creator, 'username', creator)
			if isinstance(creator, six.string_types):
				return to_unicode(creator.lower())
		except (TypeError):
			pass
		return None

	def value(self, context=None):
		context = self.context if context is None else context
		result = 	self._get_creator(context, 'creator') \
				 or self._get_creator(context, 'Creator') \
				 or SYSTEM_USER_NAME
		return result

@interface.implementer(INTIIDValue)
class _DefaultNTIIDValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		result = getattr(context, 'ntiid', None) or getattr(context, 'NTIID', None)
		return to_unicode(result) if result else None

@interface.implementer(IMimeTypeValue)
class _DefaultMimeTypeValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		context = IContentTypeAware(context, context)
		result = getattr(context, 'mimeType', None) or getattr(context, 'mime_type', None)
		return to_unicode(result) if result else None
DefaultObjectMimeTypeValue = _DefaultMimeTypeValue  # export

@interface.implementer(ICreatedTimeValue)
class _DefaultCreatedTimeValue(_BasicAttributeValue):

	attribute = 'createdTime'
	interface = ICreatedTime

	def value(self, context=None):
		context = self.context if context is None else context
		context = self.interface(context, context)
		if context is not None:
			result = getattr(context, self.attribute, None) or 0
			result = SolrDatetime.convert(result)
			return SolrDatetime.toUnicode(result) if result else None
		return None

@interface.implementer(ILastModifiedValue)
class _DefaultLastModifiedValue(_DefaultCreatedTimeValue):
	attribute = 'lastModified'
	interface = ILastModified

@interface.implementer(IIDValue)
class _DefaultIDValue(_BasicAttributeValue):

	@classmethod
	def _norm(cls, x):
		return re.sub('[^\x00-\x7F]', '_', re.sub(' ', '_', re.sub('!', '', x)))

	@classmethod
	def _type(cls, x):
		return x.split('.')[-1]

	@classmethod
	def _semt(cls, x):
		dt = SolrDatetime.convert(x)
		return "%s%sS" % (dt.year, int(ceil(dt.month / 6.0)))

	@classmethod
	def createdTime(self, context):
		adapted = ICreatedTimeValue(context, None)
		value = adapted.value() if adapted is not None else None
		return value or ZERO_DATETIME

	@classmethod
	def creator(self, context):
		adapted = ICreatorValue(context, None)
		value = adapted.value() if adapted is not None else None
		return value or SYSTEM_USER_NAME

	@classmethod
	def mimeType(self, context):
		adapted = IMimeTypeValue(context, None)
		value = adapted.value() if adapted is not None else None
		return value or 'unknown'

	@classmethod
	def prefix(cls, context):
		result = []
		for source, convert in ((cls.createdTime, cls._semt),
								(cls.creator, cls._norm),
								(cls.mimeType, cls._type)):
			value = convert(source(context))
			result.append(value)
		return '%s!=' % '-'.join(result)

	def value(self, context=None):
		context = self.context if context is None else context
		try:
			initds = component.getUtility(IIntIds)
			uid = initds.queryId(context)
			uid = "%s%s" % (self.prefix(context), uid) if uid is not None else None
			return to_unicode(uid) if uid is not None else None
		except (LookupError, KeyError):
			pass
		return None
DefaultObjectIDValue = _DefaultIDValue  # Export

@interface.implementer(IContainerIdValue)
class _DefaultContainerIdValue(_BasicAttributeValue):

	_IGNORED_TYPES = {TYPE_OID, TYPE_UUID, TYPE_INTID}

	def value(self, context=None):
		context = self.context if context is None else context
		contained = INTIContained(context, None)
		if contained is not None:
			cid = contained.containerId
			if		is_ntiid_of_types(cid, self._IGNORED_TYPES) \
				and not ICommentPost.providedBy(context):
				return None
			else:
				return (to_unicode(cid),)
		return None

@interface.implementer(IInReplyToValue)
class _DefaultInReplyToValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		result = getattr(context, "inReplyTo", None)
		return to_unicode(result.lower()) if result else None

@interface.implementer(ISharedWithValue)
class _DefaultSharedWithValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		sharedWith = getattr(context, "sharedWith", None)
		if sharedWith is not None:
			sharedWith = tuple(to_unicode(x.lower()) for x in sharedWith)
		return sharedWith

@interface.implementer(ITaggedToValue)
class _DefaultTaggedToValue(_BasicAttributeValue):

	# Tags are normally lower cased, but depending on when we get called
	# it's vaguely possible that we might see an upper-case value?
	_ENTITY_TYPES = {TYPE_NAMED_ENTITY, TYPE_NAMED_ENTITY.lower(),
					 TYPE_MEETINGROOM, TYPE_MEETINGROOM.lower()}

	def value(self, context=None):
		context = self.context if context is None else context
		context = IUserTaggedContent(context, None)
		if context is None:
			return None
		raw_tags = context.tags
		if not raw_tags:
			return None

		username_tags = set()
		for raw_tag in raw_tags:
			if is_ntiid_of_types(raw_tag, self._ENTITY_TYPES):
				entity = find_object_with_ntiid(raw_tag)
				if entity is not None:
					# We actually have to be a bit careful here; we only want
					# to catch certain types of entity tags, those that are either
					# to an individual or those that participate in security
					# relationships; (e.g., it doesn't help to use a regular FriendsList
					# since that is effectively flattened).
					# Currently, this abstraction doesn't exactly exist so we
					# are very specific about it. See also :mod:`sharing`
					if IUser.providedBy(entity):
						username_tags.add(entity.username)
					elif IDynamicSharingTargetFriendsList.providedBy(entity):
						username_tags.add(entity.NTIID)
		return tuple(username_tags)

@interface.implementer(IIsTopLevelContentValue)
class _DefaultIsTopLevelContentValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		# TODO: This is messy
		# NOTE: This is referenced by persistent objects, must stay
		if getattr(context, '__is_toplevel_content__', False):
			return True

		if IModeledContent.providedBy(context):
			if IFriendsList.providedBy(context) or IDevice.providedBy(context):
				# These things are modeled content, for some reason
				return False
			if IPersonalBlogEntryPost.providedBy(context):
				return bool(context.sharedWith)

			# HeadlinePosts (which are IMutedInStream) are threadable,
			# but we don't consider them top-level. (At this writing,
			# we don't consider the containing Topic to be top-level
			# either, because it isn't IModeledContent.)
			elif IHeadlinePost.providedBy(context):
				return False

			if IInspectableWeakThreadable.providedBy(context):
				return bool(not context.isOrWasChildInThread())
			if IThreadable.providedBy(context):
				return bool(context.inReplyTo is None)
			return True
		return None # no index

@interface.implementer(IIsDeletedObjectValue)
class _DefaultIsDeletedObjectValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		result = IDeletedObjectPlaceholder.providedBy(context)
		return True if result else None # no index

@interface.implementer(IIsUserGeneratedDataValue)
class _DefaultIsUserGeneratedDataValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		return IUserGeneratedData.providedBy(context)

@interface.implementer(IMetadataDocument)
class MetadataDocument(SchemaConfigured):
	createDirectFieldProperties(IMetadataDocument)

	mimeType = mime_type = u'application/vnd.nextthought.solr.metadatadocument'

@interface.implementer(IMetadataDocument)
def _MetadataDocumentCreator(obj, factory=MetadataDocument):
	return document_creator(obj, factory=factory, provided=IMetadataDocument)
