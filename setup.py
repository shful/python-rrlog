from __future__ import print_function
import setuptools
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

import rrlog

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
            
    return sep.join(buf)
   

long_description = read('README.txt', 'doc/CHANGES.txt')


class PyTest(TestCommand):
	
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True


    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


# Topic :: Trove Classification see https://pypi.python.org/pypi?%3Aaction=list_classifiers
setuptools.setup(
    name='rrlog',
    version=rrlog.__version__,
    url='http://github.com/shful/python-rrlog/',
    license='MIT License',
    author='Ruben Reifenberg',
    tests_require=['pytest'],
	install_requires=[
		],
    cmdclass={'test': PyTest},
    author_email='source.rr@reifenberg.de',
    description='Remote log and log rotation done instantly.',
    long_description=long_description,
    packages=[
		'rrlog',
		'rrlog.server',
		'rrlog.test',
		],
    include_package_data=True,
    platforms='any',
    test_suite='rrlog.test',
    classifiers = [
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.4',
		'Programming Language :: Python :: 2.5',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: System :: Logging',
        ],
    extras_require={
		'testing': ['pytest'],
		'database': ['SQLAlchemy>=0.3.2'],
    }
)