#!/usr/bin/env python
import sys
from setuptools import setup, find_packages

exec(open("cfnexec/version.py").read())

with open("README.md", "r") as fh:
    long_description = fh.read()

version = sys.version_info[:2]
if version < (3, 7):
    print('cfn-exec requires Python version 3.7 or later' +
        ' ({}.{} detected).'.format(*version))
    sys.exit(-1)

setup (
    name='cfnexec',
    version=__version__,
    description='This is Wrapper tool for aws cloudformation create stack.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Takenori Kusaka',
    author_email='takenori.kusaka@gmail.com',
    url='https://github.com/Takenori-Kusaka/cfn-exec',
    license='MIT',
    packages=find_packages(),
    zip_safe=True,
    keywords='aws',
    include_package_data=True,
    install_requires=[
        'requests>=2.27.1',
        'awscli>=1.22.77'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={'console_scripts': [
        'cfn-exec = cfnexec.main:main'
    ]}
)