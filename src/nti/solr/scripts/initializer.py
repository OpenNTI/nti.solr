#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os
import sys
import time
import logging
import argparse
import functools
import transaction

import zope.exceptions

from zope import component

from zope.intid.interfaces import IIntIds

from zope.event import notify

from ZODB.POSException import POSError

from nti.contentlibrary.interfaces import IContentPackage

from nti.dataserver.interfaces import IEntity
from nti.dataserver.interfaces import IDeletedObjectPlaceholder
from nti.dataserver.interfaces import IDataserverTransactionRunner

from nti.dataserver.utils import run_with_dataserver
from nti.dataserver.utils.base_script import create_context

from nti.site.site import getSite

from nti.solr.interfaces import IndexObjectEvent
try:
	from nti.contenttypes.courses.interfaes import ICourseInstance
	MIGRATE_IFACES = (IContentPackage, ICourseInstance, IEntity)
except ImportError:
	MIGRATE_IFACES = (IContentPackage, IEntity)

#: How often to log progress
LOG_ITER_COUNT = 1000
DEFAULT_COMMIT_BATCH_SIZE = 2000

def _all_objects_intids(users, last_oid):
	obj = intids = component.getUtility(IIntIds)
	usernames = {getattr(user, 'username', user).lower() for user in users or ()}

	# These should be in order.
	valid_intids = (x for x in intids if x > last_oid )
	for uid in valid_intids:
		try:
			obj = intids.getObject(uid)
			if IEntity.providedBy(obj):
				if not usernames or obj.username in usernames:
					yield uid, obj
			else:
				creator = getattr(obj, 'creator', None)
				creator = getattr(creator, 'username', creator)
				try:
					creator = creator.lower() if creator else ''
				except AttributeError:
					pass
				if	not IDeletedObjectPlaceholder.providedBy(obj) and \
					(not usernames or creator in usernames):
					yield uid, obj
		except (TypeError, POSError) as e:
			logger.error("Error processing object %s(%s); %s", type(obj), uid, e)

class _SolrInitializer(object):

	def __init__(self, usernames, last_oid, last_oid_file, batch_size, site_names=()):
		self.usernames = usernames
		self.last_oid = last_oid
		self.last_oid_file = last_oid_file
		self.batch_size = batch_size
		self.site_names = site_names

	def process_obj(self, obj):
		# Only process objects implementing one of our white-listed interfaces.
		for iface in MIGRATE_IFACES:
			if iface.providedBy( obj ):
				#logger.info( '[%s] Processing %s', getSite().__name__, obj )
				notify( IndexObjectEvent( obj ) )
				return True
		return False

	def init_solr(self):
		count = 0
		for ds_id, obj in _all_objects_intids(self.usernames, self.last_oid):
			if self.process_obj(obj):
				count += 1
				self.last_oid = ds_id
				if count % LOG_ITER_COUNT == 0:
					logger.info('[%s] Processed %s objects...', getSite().__name__, count)
					transaction.savepoint(optimistic=True)
			if self.batch_size and count > self.batch_size:
				break
		return count

	def __call__(self):
		logger.info('Initializing solr intializer (username_filter=%s) (last_oid=%s) '
					'(batch_size=%s) (site=%s)', len(self.usernames), self.last_oid,
					self.batch_size, self.site_names)
		now = time.time()
		total = 0

		transaction_runner = component.getUtility(IDataserverTransactionRunner)
		if self.site_names:
			transaction_runner = functools.partial(transaction_runner,
												   site_names=self.site_names)

		while True:
			last_valid_id = self.last_oid
			try:
				count = transaction_runner(self.init_solr, retries=2, sleep=1)
				last_valid_id = self.last_oid
				total += count
				logger.info('Committed batch (%s) (last_oid=%s) (total=%s)',
							count, last_valid_id, total)

				if 		(self.batch_size and count <= self.batch_size) \
					or 	self.batch_size is None:
					break
			except KeyboardInterrupt:
				logger.info('Exiting solr initializer')
				break
			finally:
				# Store our state
				with open(self.last_oid_file, 'w+') as f:
					f.write(str(last_valid_id))

		elapsed = time.time() - now
		logger.info("Total objects processed (size=%s) (time=%s)", total, elapsed)

class Processor(object):

	def create_arg_parser(self):
		arg_parser = argparse.ArgumentParser(description="Create a user-type object")
		arg_parser.add_argument('--usernames', dest='usernames',
								help="The usernames to migrate")
		arg_parser.add_argument('--env_dir', dest='env_dir',
								help="Dataserver environment root directory")
		arg_parser.add_argument('--batch_size', dest='batch_size',
								help="Commit after each batch")
		arg_parser.add_argument('--site', dest='site', help="request SITE")
		arg_parser.add_argument('-v', '--verbose', help="Be verbose",
								action='store_true', dest='verbose')
		return arg_parser

	def set_log_formatter(self, args):
		ei = '%(asctime)s %(levelname)-5.5s [%(name)s][%(thread)d][%(threadName)s] %(message)s'
		logging.root.handlers[0].setFormatter(zope.exceptions.log.Formatter(ei))

	def process_args(self, args, last_oid, last_oid_file):
		self.set_log_formatter(args)
		site_names = [getattr(args, 'site', None)]

		usernames = args.usernames
		if usernames:
			usernames = usernames.split(',')
		else:
			usernames = ()

		batch_size = DEFAULT_COMMIT_BATCH_SIZE
		if args.batch_size:
			batch_size = args.batch_size

		solr_initializer = _SolrInitializer(usernames, last_oid,
											last_oid_file, batch_size,
											site_names)
		result = solr_initializer()
		sys.exit(result)

	def __call__(self, *args, **kwargs):
		arg_parser = self.create_arg_parser()
		args = arg_parser.parse_args()

		env_dir = args.env_dir
		if not env_dir:
			env_dir = os.getenv('DATASERVER_DIR')
		if not env_dir or not os.path.exists(env_dir) and not os.path.isdir(env_dir):
			raise ValueError("Invalid dataserver environment root directory", env_dir)

		last_oid = 0
		last_oid_file = env_dir + '/data/.solr_initializer'
		if os.path.exists(last_oid_file):
			with open(last_oid_file, 'r') as f:
				file_last_oid = f.read()
				if file_last_oid:
					last_oid = int(file_last_oid)

		conf_packages = ('nti.solr', 'nti.appserver', 'nti.dataserver',)
		context = create_context(env_dir, with_library=True)

		run_with_dataserver(environment_dir=env_dir,
							xmlconfig_packages=conf_packages,
							verbose=args.verbose,
							context=context,
							use_transaction_runner=False,
							function=lambda: self.process_args(args, last_oid, last_oid_file))

def main():
	return Processor()()

if __name__ == '__main__':
	main()
