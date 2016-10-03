#!/usr/bin/env python

from setuptools import setup
import os
# import setuplib

# packages, package_data = setuplib.find_packages('crowdao')

setup(
    name='crowdao',
    version='0.1',
    description='Crowdfunding platform based on django and feincms.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    # author='Stefan Reinhard',
    # author_email='dev@feinheit.ch',
    # url='http://github.com/feinheit/zipfelchappe/',
    license='BSD License',
    platforms=['OS Independent'],
    packages=['crowdao'],
    # package_data=package_data,
    install_requires=[
      'django>=1.9',
      'feincms',
      'requests',
      'pytz',
      'django_comments',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
    ],
)
