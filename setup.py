#!/usr/bin/env python
import sys
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

version = sys.version_info[:2]
if version < (3, 7):
    print('cfnperm requires Python version 3.7 or later' +
        ' ({}.{} detected).'.format(*version))
    sys.exit(-1)

setup(name='cfnperm',
    version='0.0.1',
    description='Generates an IAM policy for the CloudFormation base describe-type\'s schema',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Takenori Kusaka',
    author_email='takenori.kusaka@gmail.com',
    url='https://github.com/Takenori-Kusaka/AWSPolicyCheckerFromCFn',
    license='MIT',
    packages=find_packages(),
    zip_safe=True,
    install_requires=[
        'boto3>=1.18.54'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
)