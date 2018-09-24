#!/usr/bin/env python3
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

long_des = ""
with open(path.join(here, 'README.md')) as f:
    long_des = f.read()

setup(
    name='FRCUploader',
    description="A YouTube Uploader with FIRST Robotics Competition in mind",
    long_description=long_des,
    long_description_content_type="text/markdown",
    url="https://github.com/NikhilNarayana/FRC-YouTube-Uploader",
    author="Nikhil Narayana",
    author_email="nikhil.narayana@live.com",
    license="GNU Public License v3.0",
    keywords='frc robotics youtube uploader',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
    ],
    entry_points=dict(console_scripts=['frcuploader = frcuploader.main:main']),
    python_requires='~=3.5',
    version='3.2.1',
    packages=["frcuploader"],
    install_requires=[
        'CacheControl',
        'google-api-python-client',
        'oauth2client',
        'Pyforms-Lite',
        'tbapy',
    ],
    data_files=[("share/frcuploader", ['frcuploader/client_secrets.json'])],
    package_data={'frcuploader': ['frcuploader/client_secrets.json']},
)
