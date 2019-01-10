.. _install:

Installation
==============

Requirements
-------------

* numpy
* astropy
* pandas
* matplotlib
* scipy
* pyyaml
* numba
* tqdm
* tornado
* pygmo==2.9
* esapy-web==0.2.1
* esapy-dispatcher==0.4
* esapy-config==0.6

From source (inside ESA network)
--------------------------------

.. code-block:: bash

    git clone https://gitlab.esa.int/sci-fv/pyxel.git

Give your ESAAD credentials.

Then, install requirements with ``pip`` using ``requirements.txt`` file inside the ``pyxel`` folder:

.. code-block:: bash

  pip install -r requirements.txt

or with ``conda``:

Download the whl files of the requirements and install them with ``conda install``.


Using Docker
-------------

Using Docker, you can just download the Pyxel Docker image and run it without installing Pyxel.

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


https://gitlab.esa.int/sci-fv/pyxel/container_registry


Pip install
-------------

.. attention::
    Not yet available!

**Pyxel** is available on the PyPI server of ESA SCI-FIV at the following
url: `<http://lab-linux-server.estec.esa.int/pyxel/>`.
By using this server, you are sure to have the latest stable version.

To install, simply use ``pip``:

.. code-block:: bash

  pip install pyxel

To upgrade pyxel to the latest version:

.. code-block:: bash

  pip install --upgrade pyxel
