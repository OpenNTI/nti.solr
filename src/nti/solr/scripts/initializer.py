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

from ZODB.POSException import POSKeyError

import zope.exceptions
import zope.browserpage

from zope import component

from zope.configuration import config
from zope.configuration import xmlconfig

from zope.container.contained import Contained

from zope.dottedname import resolve as dottedname

from zope.event import notify

from z3c.autoinclude.zcml import includePluginsDirective

from nti.contentlibrary.interfaces import IContentPackage

from nti.dataserver.utils import run_with_dataserver

from nti.dataserver.interfaces import IEntity
from nti.dataserver.interfaces import IDeletedObjectPlaceholder
from nti.dataserver.interfaces import IDataserverTransactionRunner

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

class PluginPoint(Contained):

	def __init__(self, name):
		self.__name__ = name

PP_APP = PluginPoint('nti.app')
PP_APP_SITES = PluginPoint('nti.app.sites')
PP_APP_PRODUCTS = PluginPoint('nti.app.products')

def _all_objects_intids(users, last_oid):
	obj = intids = component.getUtility(zope.intid.IIntIds)
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
		except (TypeError, POSKeyError) as e:
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

	conf_package = 'nti.appserver'

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

	def create_context(self, env_dir):
		etc = os.getenv('DATASERVER_ETC_DIR') or os.path.join(env_dir, 'etc')
		etc = os.path.expanduser(etc)

		context = config.ConfigurationMachine()
		xmlconfig.registerCommonDirectives(context)

		slugs = os.path.join(etc, 'package-includes')
		if os.path.exists(slugs) and os.path.isdir(slugs):
			package = dottedname.resolve('nti.dataserver')
			context = xmlconfig.file('configure.zcml', package=package, context=context)
			xmlconfig.include(context, files=os.path.join(slugs, '*.zcml'),
							  package=self.conf_package)

		library_zcml = os.path.join(etc, 'library.zcml')
		if not os.path.exists(library_zcml):
			raise Exception("Could not locate library zcml file %s", library_zcml)

		xmlconfig.include(context, file=library_zcml, package=self.conf_package)

		# Include zope.browserpage.meta.zcm for tales:expressiontype
		# before including the products
		xmlconfig.include(context, file="meta.zcml", package=zope.browserpage)

		# include plugins
		includePluginsDirective(context, PP_APP)
		includePluginsDirective(context, PP_APP_SITES)
		includePluginsDirective(context, PP_APP_PRODUCTS)
		return context

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

		last_oid_file = env_dir + '/data/.solr_initializer'
		last_oid = 0
		if os.path.exists(last_oid_file):
			with open(last_oid_file, 'r') as f:
				file_last_oid = f.read()
				if file_last_oid:
					last_oid = int(file_last_oid)

		conf_packages = ('nti.solr', 'nti.appserver', 'nti.dataserver',)
		context = self.create_context(env_dir)

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
