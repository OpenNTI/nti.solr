#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import six
from numbers import Number

from nti.solr import QUEUE_NAME
from nti.solr import add_queue_name

from nti.solr.utils import mimeTypeRegistry

ENTITIES_CATALOG = 'entities'
ENTITIES_QUEUE = QUEUE_NAME + '++entities'

USER_MIME_TYPE = 'application/vnd.nextthought.user'
COMMUNITY_MIME_TYPE = 'application/vnd.nextthought.community'
DFL_MIME_TYPE = 'application/vnd.nextthought.dynamicfriendslist'
FRIEND_LISTS_MIME_TYPE = 'application/vnd.nextthought.friendslist'


def _register():
    add_queue_name(ENTITIES_QUEUE)
    mimeTypeRegistry.register(DFL_MIME_TYPE, ENTITIES_CATALOG)
    mimeTypeRegistry.register(USER_MIME_TYPE, ENTITIES_CATALOG)
    mimeTypeRegistry.register(COMMUNITY_MIME_TYPE, ENTITIES_CATALOG)
    mimeTypeRegistry.register(FRIEND_LISTS_MIME_TYPE, ENTITIES_CATALOG)
    
_register()
del _register
