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

CALENDAR_EVENTS_CATALOG = 'calendarevents'
CALENDAR_EVENTS_QUEUE = QUEUE_NAME + '++calendarevents'

COURSE_CALENDAR_EVENT_MIME_TYPE = 'application/vnd.nextthought.courseware.coursecalendarevent'

logger = __import__('logging').getLogger(__name__)


def _register():
    add_queue_name(CALENDAR_EVENTS_QUEUE)
    mimeTypeRegistry.register(COURSE_CALENDAR_EVENT_MIME_TYPE, CALENDAR_EVENTS_CATALOG)
_register()
del _register
