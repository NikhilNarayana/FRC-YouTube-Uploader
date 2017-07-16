from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

long_des = ""
with open(path.join(here,'README.md'), encoding='utf-8') as f:
    long_des = f.read()

setup(
    name='frcUploader',
    description="A YouTube Uploader for FIRST Robotics Competition",
    long_description=long_des,
    url="https://github.com/NikhilNarayana/FRC-YouTube-Uploader",
    author="Nikhil Narayana",
    author_email="nikhil.narayana@live.com",
    license="GPL 3.0",
    keywords='frc robotics youtube uploader',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2.7',
    ],
    version='2.7-beta',
    packages=["frcUploader"],
    include_package_data=True,
)