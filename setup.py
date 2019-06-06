"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup

setup(
    package_data={"": ["*.glade", "*.ui", "*.acf"]},  # TODO: move this to 'setup.cfg'
)
