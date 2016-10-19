#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope.container.contained import Contained

from z3c.autoinclude.zcml import includePluginsDirective

from nti.async.utils.processor import Processor

from nti.solr import QUEUE_NAMES

class PluginPoint(Contained):

	def __init__(self, name):
		self.__name__ = name

PP_SOLR = PluginPoint('nti.solr')

class Constructor(Processor):

	def set_log_formatter(self, args):
		super(Constructor, self).set_log_formatter(args)

	def extend_context(self, context):
		includePluginsDirective(context, PP_SOLR)

	def process_args(self, args):
		setattr(args, 'redis', True)
		setattr(args, 'library', True)  # load library
		setattr(args, 'queue_names', QUEUE_NAMES)
		super(Constructor, self).process_args(args)

def main():
	return Constructor()()

if __name__ == '__main__':
	main()