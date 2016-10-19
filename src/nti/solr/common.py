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

from zope import component

from zope.component.hooks import getSite

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

def add_2_queue(name, func, obj, site=None, core=None, jid=None, **kwargs):
	adpated = IIDValue(obj, None)
	catalog = ICoreCatalog(obj, None)
	site = getSite().__name__ if site is None else site
	core = catalog.name if not core and catalog else core
	doc_id = adpated.value() if adpated is not None else None
	if doc_id and core:
		queue = get_job_queue(name)
		job = create_job(func, doc_id, site=site, core=core, **kwargs)
		job.id = '%s_%s_%s' % (datetime_isoformat(), doc_id, jid)
		queue.put(job)
		return job
	return None

def queue_add(name, func, obj, site=None, **kwargs):
	return add_2_queue(name, func, obj, site, 'added', **kwargs)

def queue_modified(name, func, obj, site=None, **kwargs):
	return add_2_queue(name, func, obj, site, 'modified', **kwargs)

def queue_remove(name, func, obj, site=None, **kwargs):
	return add_2_queue(name, func, obj, site, 'removed', **kwargs)

# job funcs

def single_index_job(doc_id, site=None, **kwargs):
	obj = object_finder(doc_id)
	catalog = ICoreCatalog(obj, None)
	if catalog is not None:
		return catalog.add(obj)

def single_unindex_job(doc_id, core, site=None, **kwargs):
	catalog = component.queryUtility(ICoreCatalog, name=core)
	if catalog is not None:
		catalog.unindex_doc(doc_id)
