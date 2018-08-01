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

EVALUATIONS_CATALOG = 'evaluations'
EVALUATIONS_QUEUE = QUEUE_NAME + '++evaluations'

logger = __import__('logging').getLogger(__name__)


def _register():
    add_queue_name(EVALUATIONS_QUEUE)
    # mimeTypes
    from nti.assessment.interfaces import ALL_EVALUATION_MIME_TYPES
    for m in ALL_EVALUATION_MIME_TYPES:
        mimeTypeRegistry.register(m, EVALUATIONS_CATALOG)
_register()
del _register
