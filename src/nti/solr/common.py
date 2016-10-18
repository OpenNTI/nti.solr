#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from datetime import datetime

import isodate

from nti.async import create_job

from nti.solr import get_factory

from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import ICoreCatalog 

from nti.solr.utils import object_finder

# queue funcs

def datetime_isoformat(now=None):
	now = now or datetime.now()
	return isodate.datetime_isoformat(now)

def get_job_queue(name):
	factory = get_factory()
	return factory.get_queue(name)

def add_2_queue(name, func, obj, jid, **kwargs):
	adpated = IIDValue(obj, None)
	doc_id = adpated.value() if adpated is not None else None
	if doc_id:
		queue = get_job_queue(name)
		job = create_job(func, doc_id, **kwargs)
		job.id = '%s_%s_%s' % (datetime_isoformat(), doc_id, jid)
		queue.put(job)
		return job
	return None

def queue_add(name, func, obj, **kwargs):
	return add_2_queue(name, func, obj, 'added', **kwargs)

def queue_modified(name, func, obj, **kwargs):
	return add_2_queue(name, func, obj, 'modified', **kwargs)

def queue_remove(name, func, obj, **kwargs):
	return add_2_queue(name, func, obj, 'removed', **kwargs)

# job funcs

def single_index_job(doc_id, **kwargs):
	obj = object_finder(doc_id)
	if obj is not None:
		catalog = ICoreCatalog(obj)
		return catalog.add(obj)

def single_unindex_job(doc_id, **kwargs):
	pass
