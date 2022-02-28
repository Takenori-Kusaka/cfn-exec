#!/usr/bin/env python
import sys
from setuptools import setup, find_packages

exec(open("cfngiam/version.py").read())

with open("README.md", "r") as fh:
    long_description = fh.read()

version = sys.version_info[:2]
if version < (3, 7):
    print('cfn-giam requires Python version 3.7 or later' +
        ' ({}.{} detected).'.format(*version))
    sys.exit(-1)

setup (
    name='cfngiam',
    version=__version__,
    description='Generates an IAM policy for the CloudFormation base describe-type\'s schema',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Takenori Kusaka',
    author_email='takenori.kusaka@gmail.com',
    url='https://github.com/Takenori-Kusaka/cfn-giam',
    license='MIT',
    packages=["cfngiam"],
    zip_safe=True,
    keywords='aws',
    install_requires=[
        'boto3>=1.18.54'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={'console_scripts': [
        'cfn-giam = cfngiam.main:main'
    ]}
)