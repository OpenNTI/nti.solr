#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division

__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from nti.dataserver.interfaces import ICreatedUsername

from nti.solr.interfaces import ICreatorValue

@interface.implementer(ICreatorValue)
@component.adapts(interface.Interface)
class DefaultCreatorValue(object):
    
    __slots__ = ('context',)

    def __init__(self, context):
        self.context = context
    
    def value(self, context=None):
        context = self.context if context is None else context
        context = ICreatedUsername(context, None)
        result = context.creator_username if context is not None else None
        return result.lower() if result else None # normalize
