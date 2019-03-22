#!/usr/bin/env python
#coding=utf8

try:
    from  setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup(
        name = 'browser_agency',
        version = '1.0',
        install_requires = ['requests', 'tornado', 'pyppeteer', 'psutil'], 
        description = '浏览器请求代理',
        url = 'https://github.com/zhouxianggen/browser_agency.git', 
        author = 'zhouxianggen',
        author_email = 'zhouxianggen@gmail.com',
        classifiers = [ 'Programming Language :: Python :: 3.7',],
        packages = ['browser_agency'],
        data_files = [ 
                ('/conf/supervisor/program/', ['browser_agency.ini']),], 
        entry_points = { 'console_scripts': [
                'run_browser_agency = browser_agency.run:main', ]}   
        )

