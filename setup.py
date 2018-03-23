#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import setuptools


def long_description():
    try:
        return codecs.open('README.rst', 'r', 'utf-8').read()
    except IOError:
        return 'Long description error: Missing README.rst file'


setuptools.setup(
    name='celery-batches',
    packages=setuptools.find_packages(),
    version='0.1',
    description='Experimental task class that buffers messages and processes them as a list.',
    long_description=long_description(),
    keywords='task job queue distributed messaging actor',
    author='Percipient Networks',
    author_email='support@strongarm.io',
    url='https://github.com/percipient/celery-batches',
    license='BSD',
    platforms=['any'],
    install_requires=['celery>=4.0,<5.0'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Topic :: System :: Distributed Computing',
        'Topic :: Software Development :: Object Brokering',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
    ],
)
