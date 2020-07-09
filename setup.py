from setuptools import setup

# https://stackoverflow.com/questions/14399534/reference-requirements-txt-for-the-install-requires-kwarg-in-setuptools-setup-py

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='GeoCalc',
      version='1.00.01',
      description='An automated runner to calculate Spectral Periods from a given data input.',
      author='yaboyspence',
      install_requires=required)

