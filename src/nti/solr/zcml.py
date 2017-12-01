#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import functools

from zope import component
from zope import interface

from zope.component.zcml import utility

from zope.configuration import fields

from nti.asynchronous.interfaces import IRedisQueue
from nti.asynchronous.redis_queue import RedisQueue

from nti.asynchronous import get_job_queue as async_queue

from nti.dataserver.interfaces import IRedisClient

from nti.schema.field import Int

from nti.solr.interfaces import ISOLR
from nti.solr.interfaces import ISOLRQueueFactory

from nti.solr.model import SOLR

logger = __import__('logging').getLogger(__name__)


class IRegisterSOLR(interface.Interface):

    url = fields.TextLine(title=u"SOLR url", required=True)

    name = fields.TextLine(title=u"optional registration name",
                           required=False)

    timeout = Int(title=u"timeout", required=False)


def registerSOLR(_context, url, timeout=None, name=u''):
    assert not timeout or timeout > 0, 'Invalid SOLR timeout'
    url = url[0:-1] if url.endswith('/') else url
    factory = functools.partial(SOLR, URL=url, Timeout=timeout or None)
    utility(_context, provides=ISOLR, factory=factory, name=name)


class ImmediateQueueRunner(object):
    """
    A queue that immediately runs the given job. This is generally
    desired for test or dev mode.
    """

    def put(self, job):
        job()


@interface.implementer(ISOLRQueueFactory)
class _ImmediateQueueFactory(object):

    def get_queue(self, *unused_args, **unused_kwargs):
        return ImmediateQueueRunner()


@interface.implementer(ISOLRQueueFactory)
class _AbstractProcessingQueueFactory(object):

    queue_interface = None

    def get_queue(self, name):
        queue = async_queue(name, self.queue_interface)
        if queue is None:
            msg = "No queue exists for solr processing queue (%s)." % name
            raise ValueError(msg)
        return queue


class _SOLRProcessingQueueFactory(_AbstractProcessingQueueFactory):

    queue_interface = IRedisQueue

    def __init__(self, _context):
        from nti.solr import QUEUE_NAMES  # late bind
        for name in QUEUE_NAMES:
            queue = RedisQueue(self._redis, name)
            utility(_context, provides=IRedisQueue, component=queue, name=name)

    def _redis(self):
        return component.getUtility(IRedisClient)


def registerImmediateProcessingQueue(_context):
    logger.info("Registering immediate solr processing queue")
    factory = _ImmediateQueueFactory()
    utility(_context, provides=ISOLRQueueFactory, component=factory)


def registerProcessingQueue(_context):
    logger.info("Registering solr redis processing queue")
    factory = _SOLRProcessingQueueFactory(_context)
    utility(_context, provides=ISOLRQueueFactory, component=factory)
