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
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={'console_scripts': []},
)
