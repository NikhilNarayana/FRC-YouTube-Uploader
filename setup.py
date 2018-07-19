#!/usr/bin/env python3
from setuptools import setup, find_packages
from codecs import open
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
    version='3.1.2',
    packages=["frcuploader"],
    install_requires=[
        'AnyQt==0.0.8',
        'CacheControl==0.12.4',
        'certifi==2018.1.18',
        'chardet==3.0.4',
        'cycler==0.10.0',
        'google-api-python-client==1.6.6',
        'httplib2==0.11.3',
        'idna==2.6',
        'kiwisolver==1.0.1',
        'matplotlib==2.2.2',
        'msgpack-python==0.5.6',
        'numpy==1.14.2',
        'oauth2client==4.1.2',
        'opencv-python==3.4.0.12',
        'pyasn1==0.4.2',
        'pyasn1-modules==0.2.1',
        'PyForms==3.0.0',
        'PyOpenGL==3.1.0',
        'pyparsing==2.2.0',
        'PyQt5==5.10.1',
        'python-dateutil==2.7.2',
        'pytz==2018.4',
        'QScintilla==2.10.4',
        'requests==2.18.4',
        'rsa==3.4.2',
        'sip==4.19.8',
        'six==1.11.0',
        'tbapy==1.3.0',
        'uritemplate==3.0.0',
        'urllib3==1.22',
        'visvis==1.10.0'
    ],
    data_files=[("share/frcuploader", ['frcuploader/client_secrets.json'])],
    package_data={'frcuploader': ['frcuploader/client_secrets.json']},
)
