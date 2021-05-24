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
    version='0.5',
    description='Experimental task class that buffers messages and processes them as a list.',
    long_description=long_description(),
    long_description_content_type='text/x-rst',
    keywords='task job queue distributed messaging actor',
    author='Patrick Cloke',
    author_email='clokep@patrick.cloke.us',
    url='https://github.com/clokep/celery-batches',
    license='BSD',
    platforms=['any'],
    install_requires=['celery>=4.4,<5.2'],
    python_requires=">=3.6,",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Topic :: System :: Distributed Computing',
        'Topic :: Software Development :: Object Brokering',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
    ],
)
