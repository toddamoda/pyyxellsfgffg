"""
Pyxel detector simulation framework.
"""

from setuptools import setup, find_packages

import pyxel
import versioneer


def get_requires(filenames):
    """Get the esapy2 dependency package list.

    :param str filenames: the requirements file location
    :return: the dependency list of packages
    """
    requires = []

    for filename in filenames:
        with open(filename) as file_obj:
            for line in file_obj:
                line = line.strip()

                if line.startswith('--') or line.startswith('#') or line.startswith('-r') or not line:
                    continue

                requires.append(line)

    return requires


setup(
    name=pyxel.__appname__,
    version=versioneer.get_version(),
    description=versioneer.get_cmdclass(),
    long_description=open('README.rst').read(),
    author=pyxel.__author__,
    author_email=pyxel.__author_email__,
    url='http://www.sci.esa.int/pyxel',
    license='MIT',
    keywords='esa',
    install_requires=get_requires('requirements.txt'),
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    package_data={'': ['*.glade', '*.ui', '*.acf']},
    entry_points={'console_scripts': []},
)
