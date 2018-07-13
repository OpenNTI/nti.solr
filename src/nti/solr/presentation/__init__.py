#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from itertools import chain

from zope import component

from nti.solr import QUEUE_NAME
from nti.solr import add_queue_name

from nti.solr.utils import mimeTypeRegistry

ASSETS_CATALOG = 'assets'
TRANSCRIPTS_CATALOG = 'transcripts'

ASSETS_QUEUE = QUEUE_NAME + '++assets'
TRANSCRIPTS_QUEUE = QUEUE_NAME + '++transcripts'

NTI_TRANSCRIPT_MIME_TYPE = 'application/vnd.nextthought.ntitranscript'
AUDIO_TRANSCRIPT_MIME_TYPE = 'application/vnd.nextthought.audiotranscript'
VIDEO_TRANSCRIPT_MIME_TYPE = 'application/vnd.nextthought.videotranscript'


def _register():
    add_queue_name(ASSETS_QUEUE)
    add_queue_name(TRANSCRIPTS_QUEUE)

    # transcripts
    mimeTypeRegistry.register(NTI_TRANSCRIPT_MIME_TYPE, TRANSCRIPTS_CATALOG)
    mimeTypeRegistry.register(AUDIO_TRANSCRIPT_MIME_TYPE, TRANSCRIPTS_CATALOG)
    mimeTypeRegistry.register(VIDEO_TRANSCRIPT_MIME_TYPE, TRANSCRIPTS_CATALOG)

    # assets
    from nti.app.products.courseware_ims.lti import LTI_EXTERNAL_TOOL_ASSET_MIMETYPE
    from nti.contenttypes.presentation import AUDIO_MIME_TYPES
    from nti.contenttypes.presentation import VIDEO_MIME_TYPES
    from nti.contenttypes.presentation import TIMELINE_MIME_TYPES
    from nti.contenttypes.presentation import RELATED_WORK_REF_MIME_TYPES
    for m in chain(AUDIO_MIME_TYPES,
                   VIDEO_MIME_TYPES,
                   TIMELINE_MIME_TYPES,
                   RELATED_WORK_REF_MIME_TYPES,
                   (LTI_EXTERNAL_TOOL_ASSET_MIMETYPE,)):
        mimeTypeRegistry.register(m, ASSETS_CATALOG)
_register()
del _register
