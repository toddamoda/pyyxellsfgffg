#   --------------------------------------------------------------------------
#   Copyright 2017 SRE-F, ESA (European Space Agency)
#       Hans Smit <Hans.Smit@esa.int>
#       Frederic Lemmel <Frederic.Lemmel@esa.int>
#
#   This is restricted software and is only to be used with permission
#   from the author, or from ESA.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#   THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.
#   --------------------------------------------------------------------------

from setuptools import setup, find_packages

import pyxel
import versioneer


def get_requires(filenames):
    """ Get the esapy2 dependency package list.

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
    url='http://www.esa.int',
    license='MIT',
    keywords='esa',
    install_requires=get_requires(['requirements.txt']),
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
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points={'console_scripts': []},
)