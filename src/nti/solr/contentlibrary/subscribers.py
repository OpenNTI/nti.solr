#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component

from zope.security.management import queryInteraction

from nti.contentlibrary.interfaces import IContentUnit
from nti.contentlibrary.interfaces import IContentPackage
from nti.contentlibrary.interfaces import IGlobalContentPackage 
from nti.contentlibrary.interfaces import IRenderableContentUnit
from nti.contentlibrary.interfaces import IContentPackageAddedEvent
from nti.contentlibrary.interfaces import IContentPackageRemovedEvent
from nti.contentlibrary.interfaces import IContentPackageReplacedEvent
from nti.contentlibrary.interfaces import IContentPackageRenderedEvent

from nti.publishing.interfaces import IPublishable

from nti.solr.interfaces import IIndexObjectEvent
from nti.solr.interfaces import IUnindexObjectEvent

from nti.solr.common import queue_add
from nti.solr.common import add_to_queue
from nti.solr.common import queue_remove
from nti.solr.common import queue_modified
from nti.solr.common import single_index_job
from nti.solr.common import single_unindex_job

from nti.solr.contentlibrary import CONTENT_UNITS_QUEUE

from nti.solr.contentlibrary.catalog import index_content_package
from nti.solr.contentlibrary.catalog import unindex_content_package
from nti.solr.contentlibrary.catalog import index_content_package_assets
from nti.solr.contentlibrary.catalog import unindex_content_package_assets

from nti.solr.presentation import ASSETS_QUEUE

logger = __import__('logging').getLogger(__name__)


def _get_package_and_units(package):
    result = []
    def _recur(unit):
        result.append(unit)
        for child in unit.children:
            _recur(child)
    _recur(package)
    return result


def is_published(obj):
    return not IPublishable.providedBy(obj) or obj.is_published()
isPublished = is_published


def _index_unit(unit):
    queue_add(CONTENT_UNITS_QUEUE, single_index_job, obj=unit)


def _update_unit(unit):
    queue_modified(CONTENT_UNITS_QUEUE, single_index_job, unit)


def _unindex_unit(unit):
    queue_remove(CONTENT_UNITS_QUEUE, single_unindex_job, obj=unit)


@component.adapter(IRenderableContentUnit, IContentPackageRenderedEvent)
def _contentunit_rendered(obj, unused_event=None):
    if is_published(obj):
        for unit in _get_package_and_units(obj):
            _index_unit(unit)


@component.adapter(IContentPackage, IContentPackageAddedEvent)
def _contentpackage_added(obj, unused_event=None):
    if queryInteraction() is None and IGlobalContentPackage.providedBy(obj):
        return
    for unit in _get_package_and_units(obj):
        _index_unit(unit)


@component.adapter(IContentUnit, IContentPackageReplacedEvent)
def _contentpackage_replaced(new_package, event):
    old_package = event.original
    if old_package is not None:
        for unit in _get_package_and_units(old_package):
            _unindex_unit(unit)
    for new_unit in _get_package_and_units(new_package):
        _index_unit(new_unit)


@component.adapter(IContentPackage, IContentPackageRemovedEvent)
def _contentpackage_removed(obj, unused_event=None):
    if queryInteraction() is None and IGlobalContentPackage.providedBy(obj):
        return
    for unit in _get_package_and_units(obj):
        _unindex_unit(unit)


@component.adapter(IContentUnit, IIndexObjectEvent)
def _index_contentunit(obj, unused_event=None):
    if not IContentPackage.providedBy(obj):
        _index_unit(obj)


@component.adapter(IContentUnit, IUnindexObjectEvent)
def _unindex_contentunit(obj, unused_event=None):
    if not IContentPackage.providedBy(obj):
        _unindex_unit(obj)


@component.adapter(IContentPackage, IIndexObjectEvent)
def _index_contentpackage(obj, unused_event=None):
    if is_published(obj):
        add_to_queue(CONTENT_UNITS_QUEUE,
                     index_content_package,
                     obj,
                     jid='added')
        add_to_queue(ASSETS_QUEUE,
                     index_content_package_assets,
                     obj,
                     jid='assets_added')


@component.adapter(IContentPackage, IUnindexObjectEvent)
def _unindex_contentpackage(obj, unused_event=None):
    if is_published(obj):
        add_to_queue(CONTENT_UNITS_QUEUE,
                     unindex_content_package,
                     obj,
                     jid='removed')
        add_to_queue(ASSETS_QUEUE,
                     unindex_content_package_assets,
                     obj,
                     jid='assets_removed')
