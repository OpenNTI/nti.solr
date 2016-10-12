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

from zope.intid.interfaces import IIntIds

from zope.mimetype.interfaces import IContentTypeAware

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

from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import ICreatorValue
from nti.solr.interfaces import IMimeTypeValue
from nti.solr.interfaces import ITaggedToValue
from nti.solr.interfaces import IInReplyToValue
from nti.solr.interfaces import ISharedWithValue
from nti.solr.interfaces import IContainerIdValue
from nti.solr.interfaces import ICreatedTimeValue
from nti.solr.interfaces import ILastModifiedValue
from nti.solr.interfaces import IIsDeletedObjectValue
from nti.solr.interfaces import IIsTopLevelContentValue

from nti.solr.schema import SolrDatetime

class _BasicAttributeValue(object):

	def __init__(self, context):
		self.context = context

@interface.implementer(IIDValue)
class _DefaultIDValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		try:
			initds = component.getUtility(IIntIds)
			result = initds.queryId(context)
			return unicode(result) if result is not None else None
		except (LookupError, KeyError):
			pass
		return None

@interface.implementer(ICreatorValue)
class _DefaultCreatorValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		try:
			creator = context.creator
			creator = getattr(creator, 'username', creator)
			if isinstance(creator, six.string_types):
				return creator.lower()
		except (AttributeError, TypeError):
			pass
		return None

@interface.implementer(IMimeTypeValue)
class _DefaultMimeTypeValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		context = IContentTypeAware(context, context)
		return getattr(context, 'mimeType', None) or getattr(context, 'mime_type', None)

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
				return unicode(cid)
		return None

@interface.implementer(IInReplyToValue)
class _DefaultInReplyToValue(_BasicAttributeValue):
	
	def value(self, context=None):
		context = self.context if context is None else context
		result = getattr(context, "inReplyTo", None)
		return result.lower() if result else None

@interface.implementer(ISharedWithValue)
class _DefaultSharedWithValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		sharedWith = getattr(context, "sharedWith", None)
		if sharedWith is not None:
			sharedWith = tuple(x.lower() for x in sharedWith)
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

@interface.implementer(IIsDeletedObjectValue)
class _DefaultIsDeletedObjectValue(_BasicAttributeValue):

	def value(self, context=None):
		context = self.context if context is None else context
		return IDeletedObjectPlaceholder.providedBy(context)
