.. _install:

Installation
============

Requirements
-------------

* ``python (version 3.6 or higher)``

**Dependencies available on official PyPI server:**

* ``numpy``
* ``astropy``
* ``pandas (version 0.23.0 or higher)``
* ``scipy``
* ``numba``
* ``tqdm``
* ``matplotlib``
* ``h5py``
* ``pygmo (version 2.10), optional``
* ``poppy (version 0.8.0), optional``

**Dependencies provided together with Pyxel:**

* ``dependencies/esapy_config-0.7.1-py2.py3-none-any.whl``


Install from source
-------------------

First, get access to the `Pyxel GitLab repository <https://gitlab.com/esa/pyxel>`_
from maintainers (pyxel at esa dot int).

If you can access it, then clone the GitLab repository to your computer
using ``git``:

.. code-block:: bash

    $ git clone https://gitlab.com/esa/pyxel.git

After cloning the repository, install the dependency provided together
with Pyxel using ``pip``:

.. code-block:: bash

  $ cd pyxel
  $ python3 -m pip install --user dependencies/esapy_config-0.7.1-py2.py3-none-any.whl

Then install ``pyxel`` using ``pip``. Choose one from the 4 different options below:

    * To install ``pyxel`` and all the optional dependencies (recommended):

    .. code-block:: bash

      $ python3 -m pip install --user -e ".[all]"

    * To install ``pyxel`` and the optional dependencies for *calibration mode* (``pygmo``):

    .. code-block:: bash

      $ python3 -m pip install --user -e ".[calibration]"

    * To install ``pyxel`` and the optional models (``poppy``):

    .. code-block:: bash

      $ python3 -m pip install --user -e ".[model]"

    * To install ``pyxel`` without any optional dependency:

    .. code-block:: bash

      $ python3 -m pip install --user -e .

.. note::
  If a package is not available in any PyPI server for your OS, because
  you are using Conda or Anaconda Python distribution, then you might
  have to download the Conda compatible whl file of some dependencies
  and install it manually with ``conda install``.

  If you use OSX, then you can only install ``pygmo`` with Conda.

After the installation steps above,
see :ref:`here how to run Pyxel <running_modes>`.


Install from PyPi
-----------------

TBW.


Install with Anaconda
---------------------

TBW.


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
