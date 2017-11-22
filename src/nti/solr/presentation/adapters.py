#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component
from zope import interface

from nti.contentsearch.interfaces import IResultTransformer

from nti.contenttypes.presentation.interfaces import INTITranscript

logger = __import__('logging').getLogger(__name__)


@component.adapter(INTITranscript)
@interface.implementer(IResultTransformer)
def transcript_to_media(obj):
    return obj.__parent__
