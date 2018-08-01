#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component

from nti.solr import QUEUE_NAME
from nti.solr import add_queue_name

from nti.solr.utils import mimeTypeRegistry

CONTENT_UNITS_CATALOG = 'contentunits'
CONTENT_UNITS_QUEUE = QUEUE_NAME + '++contentunits'

CONTENT_MIME_TYPE = 'application/vnd.nextthought.content'
BOOK_CONTENT_MIME_TYPE = 'application/vnd.nextthought.bookcontent'

logger = __import__('logging').getLogger(__name__)


def _register():
    add_queue_name(CONTENT_UNITS_QUEUE)
    # mimeTypes
    from nti.contentlibrary import ALL_CONTENT_MIMETYPES
    for m in ALL_CONTENT_MIMETYPES:
        mimeTypeRegistry.register(m, CONTENT_UNITS_CATALOG)
    mimeTypeRegistry.register(CONTENT_MIME_TYPE, CONTENT_UNITS_CATALOG)
    mimeTypeRegistry.register(BOOK_CONTENT_MIME_TYPE, CONTENT_UNITS_CATALOG)
_register()
del _register
