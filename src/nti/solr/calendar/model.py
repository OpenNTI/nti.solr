#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.solr.calendar import CALENDAR_EVENTS_CATALOG

from nti.solr.interfaces import ICalendarEventCatalog

from nti.solr.calendar.interfaces import ICalendarEventDocument

from nti.solr.lucene import lucene_escape

from nti.solr.metadata import MetadataCatalog
from nti.solr.metadata import MetadataDocument

logger = __import__('logging').getLogger(__name__)


@interface.implementer(ICalendarEventDocument)
class CalendarEventDocument(MetadataDocument):

    createDirectFieldProperties(ICalendarEventDocument)

    mimeType = mime_type = 'application/vnd.nextthought.solr.calendareventdocument'


@interface.implementer(ICalendarEventCatalog)
class CalendarEventCatalog(MetadataCatalog):

    name = CALENDAR_EVENTS_CATALOG
    document_interface = ICalendarEventDocument

    def build_from_search_query(self, query, **kwargs):  # pylint: disable=arguments-differ
        term, fq, params = MetadataCatalog.build_from_search_query(self, query, **kwargs)
        if 'mimeType' not in fq:
            types = self.get_mime_types(self.name)
            fq.add_or('mimeType', [lucene_escape(x) for x in types])
        return term, fq, params

    def clear(self, commit=None):
        types = self.get_mime_types(self.name)
        q = "mimeType:(%s)" % self._OR_.join(lucene_escape(x) for x in types)
        commit = self.auto_commit if commit is None else bool(commit)
        self.client.delete(q=q, commit=commit)
    reset = clear
