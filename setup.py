from distutils.core import setup

setup(
    name='frcUploader',
    description="A YouTube Uploader for FIRST Robotics Competition",
    url="https://github.com/NikhilNarayana/FRC-YouTube-Uploader",
    author="Nikhil Narayana",
    license="GPL 3.0",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2.7',
    ],
    version='2.5',
    packages=['start','addTBAToDescription','updatePlaylistThumbnails'],
)