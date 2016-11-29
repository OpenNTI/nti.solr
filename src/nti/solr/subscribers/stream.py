#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from nti.dataserver.interfaces import SC_SHARED
from nti.dataserver.interfaces import SC_CREATED
from nti.dataserver.interfaces import SC_DELETED
from nti.dataserver.interfaces import SC_MODIFIED

from nti.dataserver.interfaces import IUser
from nti.dataserver.interfaces import IEntity
from nti.dataserver.interfaces import IReadableShared
from nti.dataserver.interfaces import ITargetedStreamChangeEvent

from nti.dataserver.users import Entity

from nti.solr.subscribers.userdata import index_userdata

_changeType_events = (SC_CREATED, SC_SHARED, SC_MODIFIED)

@component.adapter(ITargetedStreamChangeEvent)
def onChange(event):
	change = event.object
	target = event.target
	changeType, changeObject = change.type, change.object
	if not IEntity.providedBy(target):
		entity = Entity.get_entity(str(target))
	else:
		entity = target

	should_process = IUser.providedBy(entity)
	if should_process:
		if 		changeType in _changeType_events \
			and IReadableShared.providedBy(changeObject):
			should_process = changeObject.isSharedDirectlyWith(entity)

	if should_process:
		if changeType != SC_DELETED:
			index_userdata(changeObject, None)

	return should_process