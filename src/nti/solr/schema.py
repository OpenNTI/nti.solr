#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import time
import numbers
from datetime import date
from datetime import datetime

import pytz

import six

from zope import interface

from zope.schema import Field
from zope.schema import Orderable

from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import ConstraintNotSatisfied

from nti.externalization.datetime import datetime_from_string

DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IDatetime, IFromUnicode)
class SolrDatetime(Orderable, Field):

    __doc__ = IDatetime.__doc__

    _type = datetime

    def __init__(self, *args, **kw):
        super(SolrDatetime, self).__init__(*args, **kw)

    @staticmethod
    def convert(value):
        if isinstance(value, six.string_types):
            return SolrDatetime.fromUnicode(value)
        elif isinstance(value, numbers.Number):
            return datetime.fromtimestamp(value, pytz.utc)
        elif isinstance(value, datetime):
            return value
        elif isinstance(value, date):
            ts = time.mktime(value.timetuple())
            return datetime.fromtimestamp(ts, pytz.utc)
        return None

    def _validate(self, value):
        try:
            converted = self.convert(value)
        except ValueError:
            raise ConstraintNotSatisfied(value, self.__name__)
        Field._validate(self, converted)

    # pylint: disable=arguments-differ

    def get(self, obj):
        value = getattr(obj, self.__name__)
        if value is not None:
            return self.toUnicode(value)
        return None

    def query(self, obj, default=None):
        value = getattr(obj, self.__name__, default)
        if value is not None:
            return self.toUnicode(value)
        return None

    def set(self, obj, value):
        value = self.convert(value)
        Field.set(self, obj, value)

    @staticmethod
    def fromUnicode(s):
        return datetime_from_string(s)

    @staticmethod
    def toUnicode(value):
        value = SolrDatetime.convert(value)
        return value.astimezone(pytz.utc).strftime(DATE_FORMAT)
