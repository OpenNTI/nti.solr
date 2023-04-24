import codecs
from setuptools import setup, find_packages

entry_points = {
}

TESTS_REQUIRE = [
    'fakeredis',
    'fudge',
    'nose',
    'nti.testing',
    'zope.dottedname',
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
    long_description=(_read('README.rst') + '\n\n' + _read("CHANGES.rst")),
    license='Apache',
    keywords='solr index',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    url="https://github.com/OpenNTI/nti.solr",
    zip_safe=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    namespace_packages=['nti'],
    tests_require=TESTS_REQUIRE,
    install_requires=[
        'setuptools',
        'BTrees',
        'gevent',
        'isodate',
	'nti.assessment',
        'nti.asynchronous',
        'nti.base',
        'nti.common',
        'nti.contentfragments',
        'nti.contentindexing',
	'nti.contentlibrary',
        'nti.contentprocessing',
	'nti.contenttypes.calendar',
        'nti.contenttypes.presentation',
        'nti.coremetadata',
	'nti.dataserver',
        'nti.externalization',
        'nti.ntiids',
        'nti.property',
        'nti.publishing',
        'nti.schema',
        'nti.site',
        'nti.traversal',
        'nti.zope_catalog',
        'pyparsing',
        'pysolr',
        'pytz',
        'six',
        'z3c.autoinclude',
        'zc.intid',
        'zope.cachedescriptors',
        'zope.component',
        'zope.configuration',
        'zope.event',
        'zope.index',
        'zope.interface',
        'zope.intid',
        'zope.lifecycleevent',
        'zope.location',
        'zope.mimetype',
        'zope.schema',
    ],
     extras_require={
        'test': TESTS_REQUIRE,
        'docs': [
            'Sphinx',
            'repoze.sphinx.autointerface',
            'sphinx_rtd_theme',
        ],
    },
    entry_points=entry_points,
)
