#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from nti.solr import QUEUE_NAME
from nti.solr import add_queue_name

from nti.solr.utils import mimeTypeRegistry

COURSES_CATALOG = 'courses'
COURSES_QUEUE = QUEUE_NAME + '++courses'

COURSE_MIME_TYPE = 'application/vnd.nextthought.courses.courseinstance'
CATALOG_ENTRY_MIME_TYPE = 'application/vnd.nextthought.courses.coursecatalogentry'
CATALOG_LEGACY_ENTRY_MIME_TYPE = 'application/vnd.nextthought.courses.coursecataloglegacyentry'

logger = __import__('logging').getLogger(__name__)


def _register():
    add_queue_name(COURSES_QUEUE)
    mimeTypeRegistry.register(COURSE_MIME_TYPE, COURSES_CATALOG)
    mimeTypeRegistry.register(CATALOG_ENTRY_MIME_TYPE, COURSES_CATALOG)
    mimeTypeRegistry.register(CATALOG_LEGACY_ENTRY_MIME_TYPE, COURSES_CATALOG)
_register()
del _register
