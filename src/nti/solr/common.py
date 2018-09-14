#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from datetime import datetime

import isodate

import six

from zope import component

from zope.component.hooks import getSite
from zope.component.hooks import site as current_site

from nti.asynchronous import create_job

from nti.contenttypes.presentation.interfaces import INTIMedia
from nti.contenttypes.presentation.interfaces import INTIDocketAsset
from nti.contenttypes.presentation.interfaces import IAssetTitleDescribed

from nti.dataserver.interfaces import IDataserver

from nti.site.site import get_site_for_site_names

from nti.site.transient import TrivialSite

from nti.solr import get_factory

from nti.solr.interfaces import IIDValue
from nti.solr.interfaces import ICoreCatalog

from nti.solr.lucene import lucene_escape

from nti.solr.userdata import USERDATA_CATALOG

from nti.solr.utils import object_finder

logger = __import__('logging').getLogger(__name__)


# queue funcs


def get_site(site_name=None):
    if site_name is None:
        site = getSite()
        site_name = site.__name__ if site is not None else None
    return site_name


def datetime_isoformat(now=None):
    now = now or datetime.now()
    return isodate.datetime_isoformat(now)


def get_job_queue(name):
    factory = get_factory()
    return factory.get_queue(name)


def put_job(name, func, jid, *args, **kwargs):
    queue = get_job_queue(name)
    job = create_job(func, *args, **kwargs)
    job.id = jid
    queue.put(job)
    return job


def add_to_queue(name, func, obj, site=None, core=None, jid=None, **kwargs):
    site = get_site(site)
    adpated = IIDValue(obj, None)
    catalog = ICoreCatalog(obj, None)
    core = catalog.name if not core and catalog else core
    # pylint: disable=too-many-function-args
    doc_id = adpated.value() if adpated is not None else None
    if doc_id and core and site:
        jid = '%s_%s' % (doc_id, jid)
        return put_job(name, func, jid=jid, source=doc_id, site=site, core=core, **kwargs)
    return None
add_2_queue = add_to_queue  # BWC


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


def single_index_job(source, site=None, **unused_kwargs):
    job_site = get_job_site(site)
    with current_site(job_site):
        obj = object_finder(source)
        catalog = ICoreCatalog(obj, None)
        if catalog is not None:
            # pylint: disable=too-many-function-args
            return catalog.index_doc(source, obj)


def single_unindex_job(source, core, site=None, **unused_kwargs):
    job_site = get_job_site(site)
    with current_site(job_site):
        catalog = component.queryUtility(ICoreCatalog, name=core)
        if catalog is not None:
            catalog.unindex_doc(source)


# assets


def finder(source):
    if     isinstance(source, six.string_types) \
        or isinstance(source, six.integer_types):
        return object_finder(source)
    return source


def process_asset(obj, index=True, commit=False):
    result = 0
    if     INTIMedia.providedBy(obj) \
        or INTIDocketAsset.providedBy(obj) \
        or IAssetTitleDescribed.providedBy(obj):
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

# pylint: disable=keyword-arg-before-vararg

def index_asset(source, site=None, commit=True, *unused_args, **unused_kwargs):
    job_site = get_job_site(site)
    with current_site(job_site):
        process_asset(finder(source), index=True, commit=commit)


def unindex_asset(source, site=None, commit=True, *unused_args, **unused_kwargs):
    job_site = get_job_site(site)
    with current_site(job_site):
        process_asset(finder(source), index=False, commit=commit)


# entities


def delete_user_data(username, *unused_args, **unused_kwargs):
    catalog = component.getUtility(ICoreCatalog, name=USERDATA_CATALOG)
    catalog.delete(q="creator:%s" %
                   lucene_escape(username.lower()), commit=True)
