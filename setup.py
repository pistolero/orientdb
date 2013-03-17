from setuptools import setup, find_packages

import os.path
here = os.path.dirname(os.path.abspath(__file__))

setup(
    name = "orientdb",
    version = "0.1",
    packages = find_packages(),
    author = "Sergey Kirillov",
    author_email = "sergey.kirillov@gmail.com",
    description = "Pure Python OrientDB binary protocol adapter and Object to Graph mapper for OrientDB database.",
    url = "https://github.com/pistolero/orientdb/",
    long_description=open(os.path.join(here, 'README.md')).read().decode('utf-8'),
    keywords = 'orientdb odm',
    test_suite = 'nose.collector'
)
