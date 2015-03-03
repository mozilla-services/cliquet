import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(here, 'CHANGELOG.rst')) as f:
    CHANGELOG = f.read()


REQUIREMENTS = [
    'colander',
    'cornice',
    'six',
    'waitress',
    'cliquet[postgresql]'
]

ENTRY_POINTS = {
    'paste.app_factory': [
        'main = readinglist:main',
    ]}

setup(name='readinglist',
      version='1.0',
      description='readinglist',
      long_description=README + "\n\n" + CHANGELOG,
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
      ],
      keywords="web services",
      author='Mozilla Services',
      author_email='services-dev@mozilla.com',
      url='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=REQUIREMENTS,
      entry_points=ENTRY_POINTS)
