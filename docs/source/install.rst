.. _install:

Installation
==============

Requirements
-------------

* python >= 3.6

**Dependencies available on official PyPI server:**

* numpy
* astropy
* pandas
* scipy
* matplotlib
* pygmo==2.10
* poppy==0.8.0
* numba
* tqdm

**Dependencies provided together with Pyxel:**

* dependencies/esapy_config-0.7-py2.py3-none-any.whl


From source
-----------

First, get access to the `Pyxel GitLab repository <https://gitlab.com/esa/pyxel>`_
from David Lucsanyi (@david.lucsanyi).

If you can access it, then clone the GitLab repository to your computer
using ``git``:

.. code-block:: bash

    git clone https://gitlab.com/esa/pyxel.git
    cd pyxel


Installation without Anaconda
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After cloning the repository, install all the requirements with
``pip`` using the ``requirements.txt`` file inside the ``pyxel``
folder:

.. code-block:: bash

  pip install -r requirements.txt

Then install locally ``pyxel``:

.. code-block:: bash

  pip install -e .

If a package is not available in any PyPI server for your OS, because
you are using Conda or Anaconda Python distribution, then you might
have to download the Conda compatible whl file of some dependencies
and install it manually with ``conda install``.


Installation with Anaconda
~~~~~~~~~~~~~~~~~~~~~~~~~~

First install the `Anaconda distribution <https://www.anaconda.com/distribution/>`_
then check if the tool ``conda`` is correctly installed:

.. code-block:: bash

  $ conda info


The second step is to create a new conda environment `pyxel-dev` and to install  
the dependencies with ``conda`` and ``pip``:

.. code-block:: bash

  $ cd pyxel

  Create conda a new environment 'pyxel-dev' 
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

Then create a new conda environemnt

.. code-block:: bash

    Create a new conda environment 'pyxel-dev'
    $ conda create --name pyxel-dev

    Activate this environment 'pyxel-dev'
    $ conda activate pyxel-dev

    Get information from this environment
    $ conda info --envs

    Install all dependencies
    $ cd pyxel
    $ conda 

    Display all conda environments
    $ conda info --envs



    Deactivate the environment
    $ conda deactivate

After these steps, you are ready to run Pyxel, see
:ref:`here how to run it <running_modes>`.




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
