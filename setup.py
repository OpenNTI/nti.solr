import codecs
from setuptools import setup, find_packages

entry_points = {
	'console_scripts': [
		"nti_solr_indexer = nti.solr.scripts.constructor:main",
	],
}

TESTS_REQUIRE = [
	'fudge',
	'nose2[coverage_plugin]',
	'nti.testing',
	'pyhamcrest',
	'z3c.baseregistry',
	'zope.testrunner',
]

def _read(fname):
	with codecs.open(fname, encoding='utf-8') as f:
		return f.read()

setup(
	name='nti.solr',
	version=_read('version.txt').strip(),
	author='Jason Madden',
	author_email='jason@nextthought.com',
	description="NTI solr",
	long_description=_read('README.rst'),
	license='Apache',
	keywords='solr',
	classifiers=[
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: Implementation :: CPython',
		'Programming Language :: Python :: Implementation :: PyPy',
	],
	zip_safe=True,
	packages=find_packages('src'),
	package_dir={'': 'src'},
	include_package_data=True,
	namespace_packages=['nti'],
	tests_require=TESTS_REQUIRE,
	install_requires=[
		'setuptools',
		'pyparsing',
		'pysolr',
		'nti.async',
		'nti.contentindexing',
		'nti.contentprocessing',
		'nti.externalization'
	],
	extras_require={
		'test': TESTS_REQUIRE,
	},
	entry_points=entry_points,
)
