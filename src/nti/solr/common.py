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

def datetime_isoformat(now=None):
	now = now or datetime.now()
	return isodate.datetime_isoformat(now)

def get_job_queue(name):
	factory = get_factory()
	return factory.get_queue(name)

def add_2_queue(name, obj):
	pass

def queue_add(name, func, obj, **kwargs):
	adpated = IIDValue(obj, None)
	doc_id = adpated.value() if adpated is not None else None
	if doc_id:
		queue = get_job_queue(name)
		job = create_job(func, obj, **kwargs)
		job.id = '%s_%s_added' % (datetime_isoformat(), doc_id)
		queue.put(job)

def queue_modified(name, obj):
	pass

def queue_remove(name, func, obj):
	pass

def single_index_job(obj):
	catalog = ICoreCatalog(obj)
	return catalog.add(obj)
