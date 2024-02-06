=============
Running Pyxel
=============

Pyxel can be run either from command line or used as a library, for example in Jupyter notebooks.

.. note::

    Once you've installed Pyxel, you can download directly some examples with command:

    .. code-block:: bash

       pyxel download-examples

       or

       python -m pyxel download-examples


    These examples will be saved in a new sub-folder ``pyxel-examples``.
    You can find more information in :doc:`examples`.


Running Pyxel from command line
===============================

To run Pyxel on your local computer, simply run it from the command-line:

.. code-block:: bash

    pyxel run input.yaml

    or

    python -m pyxel run input.yaml

Usage:

.. code-block:: bash

    Usage: pyxel run [OPTIONS] CONFIG

      Run Pyxel with a YAML configuration file.

    Options:
      -v, --verbosity     Increase output verbosity (-v/-vv/-vvv)  [default: 0]
      -s, --seed INTEGER  Random seed for the framework.
      --help              Show this message and exit.

where

========================  =======================================  ========
``CONFIG``                defines the path of the input YAML file  required
``-s`` / ``--seed``       defines a seed for random number         optional
                          generator
``-v`` / ``--verbosity``  increases the output verbosity (-v/-vv)  optional
``-V`` / ``--version``    prints the version of Pyxel              optional
========================  =======================================  ========

Running Pyxel in jupyter notebooks
==================================

An example of running Pyxel as a library:

.. code-block:: python

    import pyxel

    configuration = pyxel.load("configuration.yaml")
    exposure = configuration.exposure
    detector = configuration.detector
    pipeline = configuration.pipeline

    pyxel.run_mode(mode=exposure, detector=detector, pipeline=pipeline)

.. Note::
   You need install a Jupyter Server yourself (e.g. Jupyter Notebook, Jupyter Lab, Jupyter Hub...).

   If you want to display all intermediate steps computed by function ``pyxel.run_mode``, you can check this link:
   `Is there a way to display all intermediate steps when a pipeline is executed ? <https://esa.gitlab.io/pyxel/doc/stable/about/FAQ.html#is-there-a-way-to-display-all-intermediate-steps-when-a-pipeline-is-executed>`_


Running Pyxel from a Docker container
=====================================

If you want to run Pyxel in a Docker container, you must first get the source code
from the `Pyxel GitLab repository <https://gitlab.com/esa/pyxel>`_.

.. code-block:: console

    git clone https://gitlab.com/esa/pyxel.git
    cd pyxel


.. Note::
    Folder ``./pyxel/volumes/notebooks`` is linked to
    folder ``/home/pyxel/jupyter/notebooks`` in the container.


Build an image
--------------

.. tab:: docker-compose

    .. code-block:: console

        # Create docker image 'pyxel_pyxel'
        docker-compose build

.. tab:: only docker

    .. code-block:: console

        # Create docker image 'pyxel'
        docker build -t pyxel .


Create and start the container
------------------------------

Run Pyxel with a Jupyter Lab server from a new docker container:

.. tab:: docker-compose

    .. code-block:: console

        # Create and start a new container 'pyxel_pyxel_1'
        docker-compose up -d

.. tab:: only docker

    .. code-block:: console

        # Create and start new container 'my_pyxel' from image 'pyxel'
        docker create -p 8888:8888 -v $PWD/volumes/notebooks:/home/pyxel/jupyter/notebooks pyxel --name my_pyxel
        docker start my_pyxel

Stop and remove the container
-----------------------------

Stop and remove a running Pyxel container.

.. tab:: docker-compose

    .. code-block:: console

        # Stop and remove container 'pyxel_pyxel_1'
        docker-compose down

.. tab:: only docker

    .. code-block:: console

        # Stop and remove container 'my_pyxel'
        docker stop my_pyxel
        docker rm my_pyxel

Check if the container is running
----------------------------------

List running containers.

.. tab:: docker-compose

    .. code-block:: console

        docker-compose ps


.. tab:: only docker

    .. code-block:: console

        docker ps


Get logs
--------

View output from the Pyxel container.

.. tab:: docker-compose

    .. code-block:: console

        # Get logs from container 'pyxel_pyxel_1'
        docker-compose logs -f


.. tab:: only docker

    .. code-block:: console

        # Get logs from container 'my_pyxel'
        docker logs -f my_pyxel
