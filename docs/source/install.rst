.. _install:

Installation
============

You can install ``pyxel`` with ``pip`` (not yet) or by installing from source.

The recommended installation method is `pip <https://pip.pypa.io/en/stable/>`_-installing
into a `virtualenv <https://hynek.me/articles/virtualenv-lives/>`_.


Requirements
-------------

* ``python >=3.6``

**Dependencies available on official PyPI server:**

* ``numpy``
* ``astropy``
* ``pandas>=0.23.0``
* ``scipy``
* ``numba``
* ``tqdm``
* ``matplotlib``
* ``h5py``
* ``pygmo>=2.10 [optional]``
* ``poppy>=0.8.0 [optional]``

**Dependencies provided together with Pyxel:**

* ``dependencies/esapy_config-*.whl``


Before you begin
----------------

Python
~~~~~~

Before you got any further, make sure you've got Python 3.6 or newer available
from your command line.

You can check this by simply running:

.. code-block:: bash

  $ python3 --version
  Python 3.7.2

  or

  $ python3.7 --version
  Python 3.7.2


On Windows, you can also try:

.. code-block:: bash

 $ py -3 --version
 Python 3.7.2

 or

 $ py -3.7 --version
 Python 3.7.2

.. note::

  Do not use command ``python``, you should use a command like ``pythonX.Y``.
  For example, to start Python 3.6, you use the command ``python3.6``.


Pip
~~~

Furthermore, you'll need to make sure pip is installed with a recent version.
You can check this by running:

.. code-block:: bash

  $ python3.7 -m pip --version
  pip 19.1.1

.. note::

  Do not use command ``pip`` but ``python -m pip``.
  For example, to start ``pip`` for Python 3.6, you use the command ``python3.6 -m pip``.

You can find more information about installing packages
at this `link <https://packaging.python.org/installing/>`_.


Install from source
-------------------

Get source code
~~~~~~~~~~~~~~~

First, get access to the `Pyxel GitLab repository <https://gitlab.com/esa/pyxel>`_
from maintainers (pyxel at esa dot int).

If you can access it, then clone the GitLab repository to your computer
using ``git``:

.. code-block:: bash

    $ git clone https://gitlab.com/esa/pyxel.git


Install requirements
~~~~~~~~~~~~~~~~~~~~

After cloning the repository, install the dependency provided together
with Pyxel using ``pip``:


.. code-block:: bash

  $ cd pyxel
  $ python3.6 -m pip install -r requirements.txt

.. note::
  This command installs all packages that cannot be found in ``pypi.org``.
  This step will disappear for future versions of ``pyxel``.

.. important::
  To prevent breaking any system-wide packages (ie packages installed for all users)
  or to avoid using command ``$ sudo pip ...`` you can do a `user installation <https://pip.pypa.io/en/stable/user_guide/#user-installs>`_.

  With the command: ``$ python3.6 -m pip install --user -r requirements.txt``


Install Pyxel
~~~~~~~~~~~~~

To install ``pyxel`` use ``pip`` locally, choose one from
the 4 different options below:


.. code-block:: bash

  $ python3.6 -m pip install -e ".[all]"            # Install everything (recommended)
  $ python3.6 -m pip install -e ".[calibration]"    # Install dependencies for 'calibration mode' (pygmo)
  $ python3.6 -m pip install -e ".[model]"          # Install dependencies for optional models (poppy)
  $ python3.6 -m pip install -e .                   # Install without any optional dependencies


..
  To install ``pyxel`` use ``pip`` locally, choose one from the 4 different options below:

    * To install ``pyxel`` and all the optional dependencies (recommended):

    .. code-block:: bash

      $ python3.6 -m pip install -e ".[all]"

    * To install ``pyxel`` and the optional dependencies for *calibration mode* (``pygmo``):

    .. code-block:: bash

      $ python3.6 -m pip install -e ".[calibration]"

    * To install ``pyxel`` and the optional models (``poppy``):

    .. code-block:: bash

      $ python3.6 -m pip install -e ".[model]"

    * To install ``pyxel`` without any optional dependency:

    .. code-block:: bash

      $ python3.6 -m pip install -e .


.. important::
  To prevent breaking any system-wide packages (ie packages installed for all users)
  or to avoid using command ``$ sudo pip ...`` you can do a `user installation <https://pip.pypa.io/en/stable/user_guide/#user-installs>`_.
  Whenvever you see the command ``$ python3.6 -m pip install ...`` then replace it
  by the command ``$ python3.6 -m pip install --user ...``.

  If ``pyxel`` is not available in your shell after installation, you will need to add
  the `user base <https://docs.python.org/3/library/site.html#site.USER_BASE>`_'s binary
  directory to your PATH.

  On Linux and MacOS the user base binary directory is typically ``~/.local``.
  You'll need to add ``~/.local/bin`` to your PATH.
  On Windows the user base binary directory is typically
  ``C:\Users\Username\AppData\Roaming\Python36\site-packages``.
  You will need to set your PATH to include
  ``C:\Users\Username\AppData\Roaming\Python36\Scripts``.
  you can find the user base directory by running
  ``python3.6 -m site --user-base`` and adding ``bin`` to the end.


After the installation steps above,
see :ref:`here how to run Pyxel <running_modes>`.


Install from PyPi
-----------------

TBW.


To upgrade ``pyxel`` to the latest version:

TBW.


Install with Anaconda
---------------------

TBW.

.. note::
  If a package is not available in any PyPI server for your OS, because
  you are using Conda or Anaconda Python distribution, then you might
  have to download the Conda compatible whl file of some dependencies
  and install it manually with ``conda install``.

  If you use OSX, then you can only install ``pygmo`` with Conda.


Using Docker
-------------

TBW.

..
    Installation with Anaconda
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    First install the `Anaconda distribution <https://www.anaconda.com/distribution/>`_
    then check if the tool ``conda`` is correctly installed:

    .. code-block:: bash

      $ conda info

    The second step is to create a new conda environment `pyxel-dev` and
    to install the dependencies with ``conda`` and ``pip``:

    .. code-block:: bash

      $ cd pyxel

      Create a new conda environment 'pyxel-dev'
      and install some dependencies from conda with `environment.yml`
      $ conda env create -f environment.yml

      Display all conda environments (only for checking)
      $ conda info --envs

      Activate the conda environment 'pyxel-dev'
      $ (pyxel-dev) conda activate pyxel-dev

      Install the other dependencies not installed by conda
      $ (pyxel-dev) pip install -r requirements.txt


    Then install ``pyxel`` in the conda environment:

    .. code-block:: bash

      $ (pyxel-dev) cd pyxel
      $ (pyxel-dev) pip install -e .

    More about the conda environments (only for information):

    .. code-block:: bash

      Deactivate the environment
      $ conda deactivate

      Remove the conda environment 'pyxel-dev'
      $ conda remove --name pyxel-dev --all

    After the installation steps above,
    see :ref:`here how to run Pyxel <running_modes>`.


    Using Docker
    -------------

    .. attention::
        Not yet available!

    Using Docker, you can just download the Pyxel Docker image and run it without
    installing Pyxel.

    How to run a Pyxel container with Docker:

    Login:

    .. code-block:: bash

      docker login gitlab.esa.int:4567

    Pull latest version of the Pyxel Docker image:

    .. code-block:: bash

      docker pull gitlab.esa.int:4567/sci-fv/pyxel

    Run Pyxel Docker container with GUI:

    .. code-block:: bash

      docker run -p 9999:9999 \
                 -it gitlab.esa.int:4567/sci-fv/pyxel:latest \
                 --gui True

    Run Pyxel Docker container in batch mode (without GUI):

    .. code-block:: bash

      docker run -p 9999:9999 \
                 -v C:\dev\work\docker:/data \
                 -it gitlab.esa.int:4567/sci-fv/pyxel:latest \
                 -c /data/settings_ccd.yaml \
                 -o /data/result.fits

    List your running Docker containers:

    .. code-block:: bash

      docker ps

    After running Pyxel container you can access it:

    .. code-block:: bash

      docker exec -it <CONTAINER_NAME> /bin/bash
