#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division

__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six

from zope import interface

from nti.solr.interfaces import ICreatorValue

@interface.implementer(ICreatorValue)
class _DefaultCreatorValue(object):
    
    __slots__ = ('context',)

    def __init__(self, context):
        self.context = context
    
    def value(self, context=None):
        context = self.context if context is None else context
        try:
            creator = context.creator
            creator = getattr(creator, 'username', creator)
            if isinstance(creator, six.string_types):
                return creator.lower()
        except (AttributeError,TypeError):
            pass
        return None
