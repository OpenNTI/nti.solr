#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from zope.intid.interfaces import IIntIdAddedEvent
from zope.intid.interfaces import IIntIdRemovedEvent

from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from nti.contentlibrary.interfaces import IContentUnit
from nti.contentlibrary.interfaces import IContentPackage

from nti.solr import ASSETS_QUEUE
from nti.solr import CONTENT_UNITS_QUEUE

from nti.solr.interfaces import IIndexObjectEvent
from nti.solr.interfaces import IUnindexObjectEvent

from nti.solr.common import queue_add
from nti.solr.common import add_to_queue
from nti.solr.common import queue_remove
from nti.solr.common import queue_modified
from nti.solr.common import single_index_job
from nti.solr.common import single_unindex_job
from nti.solr.common import index_content_package
from nti.solr.common import unindex_content_package
from nti.solr.common import index_content_package_assets
from nti.solr.common import unindex_content_package_assets

@component.adapter(IContentUnit, IIntIdAddedEvent)
def _contentunit_added(obj, event=None):
	queue_add(CONTENT_UNITS_QUEUE, single_index_job, obj)

@component.adapter(IContentUnit, IObjectModifiedEvent)
def _contentunit_modified(obj, event):
	queue_modified(CONTENT_UNITS_QUEUE, single_index_job, obj)

@component.adapter(IContentUnit, IIntIdRemovedEvent)
def _contentunit_removed(obj, event):
	queue_remove(CONTENT_UNITS_QUEUE, single_unindex_job, obj=obj)

@component.adapter(IContentUnit, IIndexObjectEvent)
def _index_contentunit(obj, event):
	if not IContentPackage.providedBy(obj):
		_contentunit_added(obj, None)

@component.adapter(IContentUnit, IUnindexObjectEvent)
def _unindex_contentunit(obj, event):
	if not IContentPackage.providedBy(obj):
		_contentunit_removed(obj, None)

@component.adapter(IContentPackage, IIndexObjectEvent)
def _index_contentpackage(obj, event):
	add_to_queue(CONTENT_UNITS_QUEUE, index_content_package, obj, jid='added')
	add_to_queue(ASSETS_QUEUE, index_content_package_assets, obj, jid='assets_added')

@component.adapter(IContentPackage, IUnindexObjectEvent)
def _unindex_contentpackage(obj, event):
	add_to_queue(CONTENT_UNITS_QUEUE, unindex_content_package, obj, jid='removed')
	add_to_queue(ASSETS_QUEUE, unindex_content_package_assets, obj, jid='assets_removed')
