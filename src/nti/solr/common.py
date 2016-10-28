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
from zope.component.hooks import site as current_site

from nti.async import create_job

from nti.contentlibrary.interfaces import IContentPackage

from nti.contenttypes.presentation.interfaces import INTIMedia
from nti.contenttypes.presentation.interfaces import INTIDocketAsset
from nti.contenttypes.presentation.interfaces import IPresentationAssetContainer
	
from nti.dataserver.interfaces import IDataserver

from nti.site.site import get_site_for_site_names

from nti.site.transient import TrivialSite

from nti.solr import get_factory
from nti.solr import primitive_types

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

def add_to_queue(name, func, obj, site=None, core=None, jid=None, **kwargs):
	adpated = IIDValue(obj, None)
	catalog = ICoreCatalog(obj, None)
	site = getSite().__name__ if site is None else site
	core = catalog.name if not core and catalog else core
	doc_id = adpated.value() if adpated is not None else None
	if doc_id and core:
		queue = get_job_queue(name)
		job = create_job(func, doc_id, site=site, core=core, **kwargs)
		job.id = '%s_%s' % (doc_id, jid)
		queue.put(job)
		return job
	return None
add_2_queue = add_to_queue # BWC

def queue_add(name, func, obj, site=None, **kwargs):
	return add_to_queue(name, func, obj, site=site, jid='added', **kwargs)

def queue_modified(name, func, obj, site=None, **kwargs):
	return add_to_queue(name, func, obj, site=site, jid='modified', **kwargs)

def queue_remove(name, func, obj, site=None, **kwargs):
	return add_to_queue(name, func, obj, site=site, jid='removed', **kwargs)

# job funcs

def get_job_site(job_site_name=None):
	old_site = getSite()
	if job_site_name is None:
		job_site = old_site
	else:
		dataserver = component.getUtility(IDataserver)
		ds_folder = dataserver.root_folder['dataserver2']
		with current_site(ds_folder):
			job_site = get_site_for_site_names((job_site_name,))

		if job_site is None or isinstance(job_site, TrivialSite):
			raise ValueError('No site found for (%s)' % job_site_name)
	return job_site

def single_index_job(doc_id, site=None, **kwargs):
	job_site = get_job_site(site)
	with current_site(job_site):
		obj = object_finder(doc_id)
		catalog = ICoreCatalog(obj, None)
		if catalog is not None:
			return catalog.index_doc(doc_id, obj)

def single_unindex_job(doc_id, core, site=None, **kwargs):
	job_site = get_job_site(site)
	with current_site(job_site):
		catalog = component.queryUtility(ICoreCatalog, name=core)
		if catalog is not None:
			catalog.unindex_doc(doc_id)

# assets

def finder(source):
	return object_finder(source) if isinstance(source, primitive_types) else source
	
def process_asset(obj, index=True, commit=False):
	result = 0
	if INTIDocketAsset.providedBy(obj) or INTIMedia.providedBy(obj):
		result += 1
		catalog = ICoreCatalog(obj)
		operation = catalog.add if index else catalog.remove
		operation(obj, commit=commit)
		if INTIMedia.providedBy(obj):
			for transcript in getattr(obj, 'transcripts', None) or ():
				result += 1
				catalog = ICoreCatalog(transcript)
				operation = catalog.add if index else catalog.remove
				operation(transcript, commit=commit)
	return result

def index_asset(source, site=None, commit=True, *args, **kwargs):
	job_site = get_job_site(site)
	with current_site(job_site):
		process_asset(finder(source), index=True, commit=commit)

def unindex_asset(source, site=None, commit=True, *args, **kwargs):
	job_site = get_job_site(site)
	with current_site(job_site):
		process_asset(finder(source), index=False, commit=commit)

# content untis/packages

def process_content_package(obj, index=True):
	def recur(unit):
		commit = IContentPackage.providedBy(unit)
		for child in unit.children or ():
			recur(child)
		catalog = ICoreCatalog(unit)
		operation = catalog.add if index else catalog.remove
		operation(unit, commit=commit)
	recur(obj)

def index_content_package(source, site=None, *args, **kwargs):
	job_site = get_job_site(site)
	with current_site(job_site):
		obj = finder(source)
		if IContentPackage.providedBy(obj):
			logger.info("Indexing %s started", obj)
			process_content_package(obj, index=True)
			logger.info("Indexing %s completed", obj)

def unindex_content_package(source, site=None, **kwargs):
	job_site = get_job_site(site)
	with current_site(job_site):
		obj = finder(source)
		if IContentPackage.providedBy(obj):
			process_content_package(obj, index=False)

def process_content_package_assets(obj, index=True):
	def recur(unit):
		collector = set()
		def recur(unit):
			container = IPresentationAssetContainer(unit, None)
			if container:
				collector.update(container.values())
			for child in unit.children or ():
				recur(child)
		size = len(collector) - 1
		for x, a in enumerate(collector):
			process_asset(a, index=index, commit=size==x)
	recur(obj)

def index_content_package_assets(source, site=None, *args, **kwargs):
	job_site = get_job_site(site)
	with current_site(job_site):
		obj = finder(source)
		if IContentPackage.providedBy(obj):
			process_content_package_assets(obj, index=True)

def unindex_content_package_assets(source, site=None, *args, **kwargs):
	job_site = get_job_site(site)
	with current_site(job_site):
		obj = finder(source)
		if IContentPackage.providedBy(obj):
			process_content_package_assets(obj, index=False)
