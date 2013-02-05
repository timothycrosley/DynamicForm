#!/usr/bin/env python

from distutils.core import setup

setup(name='DynamicForm',
      version='0.4.3',
      description='DynamicForm is an AJAX abstraction library for python - that enables different sections of a page to operate and be interacted with independently.',
      author='Timothy Crosley',
      author_email='timothy.crosley@gmail.com',
      url='http://www.dynamicform.org/',
      download_url='https://github.com/timothycrosley/DynamicForm/blob/master/dist/DynamicForm-0.4.3.tar.gz?raw=true',
      license = "GNU GPLv2",
      install_requires=['webelements>=1.0.0-alpha.4',],
      packages=['DynamicForm',],)