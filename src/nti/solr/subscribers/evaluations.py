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

from nti.assessment.interfaces import IQEvaluation

from nti.coremetadata.interfaces import IObjectPublishedEvent
from nti.coremetadata.interfaces import IObjectUnpublishedEvent

from nti.solr import EVALUATIONS_QUEUE

from nti.solr.common import queue_add
from nti.solr.common import queue_remove
from nti.solr.common import queue_modified
from nti.solr.common import single_index_job
from nti.solr.common import single_unindex_job

from nti.solr.interfaces import IIndexObjectEvent
from nti.solr.interfaces import IUnindexObjectEvent


@component.adapter(IQEvaluation, IIntIdAddedEvent)
def _evaluation_added(obj, event):
    if obj.isPublished():
        queue_add(EVALUATIONS_QUEUE, single_index_job, obj)


@component.adapter(IQEvaluation, IObjectModifiedEvent)
def _evaluation_modified(obj, event):
    if obj.isPublished():
        queue_modified(EVALUATIONS_QUEUE, single_index_job, obj)


@component.adapter(IQEvaluation, IObjectPublishedEvent)
def _evaluation_published(obj, event):
    queue_modified(EVALUATIONS_QUEUE, single_index_job, obj)


@component.adapter(IQEvaluation, IObjectUnpublishedEvent)
def _evaluation_unpublished(obj, event):
    queue_remove(EVALUATIONS_QUEUE, single_unindex_job, obj=obj)


@component.adapter(IQEvaluation, IIntIdRemovedEvent)
def _evaluation_removed(obj, event):
    queue_remove(EVALUATIONS_QUEUE, single_unindex_job, obj=obj)


@component.adapter(IQEvaluation, IIndexObjectEvent)
def _index_evaluation(obj, event):
    queue_add(EVALUATIONS_QUEUE, single_index_job, obj)


@component.adapter(IQEvaluation, IUnindexObjectEvent)
def _unindex_evaluation(obj, event):
    _evaluation_removed(obj, None)
