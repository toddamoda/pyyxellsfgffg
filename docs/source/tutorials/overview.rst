.. _introduction:

============
Introduction
============

**Pyxel** :cite:`2020:prodhomme` **is a novel, open-source, modular
Python software framework designed
to host and pipeline models (analytical, numerical, statistical) simulating
different types of detector effects on images produced by Charge-Coupled
Devices (** :term:`CCD` **), Monolithic, and Hybrid** :term:`CMOS` **imaging sensors.**

Users can provide one or more input images to Pyxel, set the detector and
model parameters via a user interface (configuration file)
and select which effects to simulate: cosmic rays, detector
Point Spread Function (PSF), electronic noises, Charge Transfer Inefficiency
(CTI), persistence, dark current, charge diffusion, optical effects, etc.
The output is one or more images including the simulated detector effects
combined.

.. figure:: _static/Pyxel-example-transparent.png
    :alt: example
    :align: center

    Examples of output images created using Pyxel.
    Left: original image;
    centre: tracks of cosmic ray protons have been added;
    right: in addition to the cosmic ray protons tracks the effects
    of lower full well capacity and charge transfer inefficiency have been added.


On top of its model hosting capabilities, the framework also provides a set
of basic image analysis tools and an input image generator as well. It also
features a parametric mode to perform parametric and sensitivity analysis,
and a model calibration mode to find optimal values of its parameters
based on a target dataset the model should reproduce.

A majority of Pyxel users are expected to be detector scientists and
engineers working with instruments - using detectors - built for astronomy
and Earth observation, who need to perform detector simulations, for example
to understand laboratory data, to derive detector design specifications for
a particular application, or to predict instrument and mission performance
based on existing detector measurements.

One of the main purposes of this new tool is to share existing resources
and avoid duplication of work. For instance, detector models
developed for a certain project could be reused by
other projects as well, making knowledge transfer easier.


Quickstart Setup
================

The best way to get started and learn Pyxel are the :doc:`examples`.


🚀 Quickstart Setup with quick installation (recommended) with `uv <https://docs.astral.sh/uv/>`_ 🚀
----------------------------------------------------------------------------------------------------

1. Install `uv <https://docs.astral.sh/uv/>`_
`````````````````````````````````````````````

The fastest way to install and try Pyxel is to use `uv <https://docs.astral.sh/uv/>`_, an extremely fast Python package
and project manager.

.. warning::

    With this method, it is not possible to install Pyxel with Calibration mode feature on Windows and Mac.
    Please install Pyxel with 'miniconda' (see below).


**There is no need to create a Python virtual environment or Conda Environment and install Python**,
`uv <https://docs.astral.sh/uv/>`_ will handle this transparently for you.

First install `uv <https://docs.astral.sh/uv/>`_ (see `here <https://docs.astral.sh/uv/#highlights>`_)
from the command line with the official standalone installer:

.. tab:: macOS and Linux

    .. code-block:: bash

        curl -LsSf https://astral.sh/uv/install.sh | sh

.. tab:: Windows

    .. code-block:: bash

        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

Then restart or open a new command line terminal.

.. tip::

    To update `uv`, you can enter the following from the command line:

    .. code-block:: bash

        $ uv self update


2. Get the current version of the last release of Pyxel
```````````````````````````````````````````````````````

Enter the following in the command line:

.. code-block:: bash

    $ uvx pyxel-sim --version
    pyxel-sim, version 2.5
    Python (CPython) 3.11.9


3. Download the tutorial notebooks
``````````````````````````````````

Then you can download the Pyxel tutorial notebooks in folder `pyxel-examples` with the following commands:

.. code-block:: bash

    $ uvx pyxel-sim download-examples
    Downloading examples: 388MB [00:08, 47.9MB/s]
    Done in folder /../pyxel-examples.


4. Run Pyxel with Jupyter lab
`````````````````````````````

Then you can start a Jupyter Lab server with the latest version of Pyxel:

.. code-block:: bash

    $ cd pyxel-examples
    $ uvx --with pyxel-sim[model] --from jupyterlab jupyter-lab

or with a Jupyter Lab server, a pre-defined version of Pyxel and Python:

.. code-block:: bash

    $ cd pyxel-examples
    $ uvx --python 3.11 --with "pyxel-sim[model]==2.5" --from jupyterlab jupyter-lab

.. info::

    You can also run Pyxel with Python `Spyder IDE <https://www.spyder-ide.org>`_:

    .. code-block:: bash

        $ cd pyxel-examples
        $ uvx --with pyxel-sim[model] spyder

    of from `IPython <https://ipython.readthedocs.io>`_

     .. code-block:: bash

        $ cd pyxel-examples
        $ uvx --with pyxel-sim[model] ipython

    or directly from the command line

    .. code-block:: bash

        $ cd pyxel-examples
        $ cd tutorial
        $ uvx pyxel-sim run exposure.yaml


🐌 Quickstart Setup with 'normal' installation with `Miniconda <https://docs.anaconda.com/miniconda>`_ 🐌
---------------------------------------------------------------------------------------------------------

For convenience we provide a pre-defined conda environment file,
so you can get additional useful packages together with Pyxel in a virtual isolated environment.

First install `Miniconda <https://docs.anaconda.com/miniconda>`_ and then just execute the following
commands in the terminal:

.. tip::

    Alternatively, you can use `Mamba <https://mamba.readthedocs.io>`_.
    Mamba is an alternative package manager that support most of conda’s command but
    offers higher installation speed and more reliable environment solutions.
    To install ``mamba`` in the Conda base environment:

    .. code-block:: bash

        conda install mamba -n base -c conda-forge

    then you can replace command ``conda`` by ``mamba``.


.. tab:: Linux, MacOS, Windows (WSL)

    .. code-block:: bash

        curl -O https://esa.gitlab.io/pyxel/doc/latest/pyxel-2.5-environment.yaml
        conda env create -f pyxel-2.5-environment.yaml

.. tab:: Windows (Powershell)

    .. code-block:: bash

        wget https://esa.gitlab.io/pyxel/doc/latest/pyxel-2.5-environment.yaml -outfile "pyxel-2.5-environment.yaml"
        conda env create -f pyxel-2.5-environment.yaml


Once the conda environment has been created you can active it using:

.. code-block:: bash

    conda activate pyxel-2.5

You can now proceed to download the Pyxel tutorial notebooks.
The total size to download is ~200 MB.

Select the location where you want to install the tutorials and datasets and
proceed with the following command to download them in folder ``pyxel-examples``:

.. code-block:: bash

    pyxel download-examples

You can run Pyxel as a package if running it as a script does not work:

.. code-block:: bash

    python -m pyxel download-examples

Finally start a notebook server by executing:

.. code-block:: bash

    cd pyxel-examples
    jupyter lab

Now, you can skip the installation guide :doc:`install` and go directly to the tutorials and
explore the examples in :doc:`examples` to learn how to use Pyxel.

Getting started
===============

Are you new to Pyxel ? This is the place to start !

1. Start with installation guide in :doc:`install`.
2. Once ready you can learn how to run Pyxel in :doc:`running`.
3. Don't forget to take a look at :doc:`get_help` page.
4. Follow the tutorials and explore the examples in :doc:`examples` to learn how to use Pyxel.
