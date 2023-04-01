#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='spotifycli',
    version='1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'spotifycli=spotifycli.spotifycli:main'
        ]
    },
    package_data={'': ['']},
    include_package_data=True,
    classifiers=[],
    install_requires=['setuptools']
)

