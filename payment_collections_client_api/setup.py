import os
# import sys
# from setuptools import setup
# from setuptools.command.test import test as test_command
from setuptools import find_packages, setup

author = 'Isaac d3vnull Thomas'
author_email = 'd3vnull@mesika.org'
url = 'https://www.mesika.org'
version = '1.0.1'


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

requires = ['pytest', 'requests', 'pycryptodomex', 'pycrypto', 'celery', 'uwsgi',
            'django', 'mesika_libs', 'unidecode', 'psycopg2', 'mesika_utils']


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
        name='payment_collections_client_api',
        author=author,
        author_email=author_email,
        url=url,
        packages=find_packages(exclude=["production_settings.py",
                                        "production.json", "development.json",
                                        "development_settings.py"]),
        scripts=['manage.py'],
        include_package_data=True,
        description='Digital Payment Collections For Clients',
        long_description=readme(),
        version=version,  # Update the version number for new releases
        install_requires=requires,
        zip_safe=True,
        classifiers=[
            'Environment :: Web Environment',
            'Framework :: Django',
            'Framework :: Django :: 2.1',
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy'
        ],
)
