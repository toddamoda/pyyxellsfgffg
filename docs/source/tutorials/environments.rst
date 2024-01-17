.. _virtualenvs:

====================
Virtual Environments
====================

We recommend to create an isolated virtual environment for each version of Pyxel,
so that you have full control over additional packages that you may use in your analysis.
This will also help you on improving reproducibility within the user community.

.. _conda_envs:

Conda Environments
==================

It is recommended to create a fresh new `Conda environment <https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html>`_
for each installation of Pyxel with ``conda`` (or ``mamba``).

For more information about Package Management with Conda see
`this link <https://the-turing-way.netlify.app/reproducible-research/renv/renv-package.html>`_
from the Turing Way (https://the-turing-way.netlify.app)

First make sure you have a recent version of ``conda`` in your base environment (this is optional):

.. code-block:: bash

    conda update -n base conda

Then, as a best practice, create a new custom conda environment (e.g. ``my-pyxel-analysis``)
rather than installing in the base conda environment with the command:

.. code-block:: bash

    conda create -n my-pyxel-analysis

Once the conda environment is created, you have to activate it:

.. code-block:: bash

    conda activate my-pyxel-analysis

After that you can install Pyxel using ``conda`` / ``mamba`` as well as
other packages you may need (in this case ``jupyterlab``):

.. note:: Don't forget to install lacosmic manually with ``pip`` (in the current conda environment)

.. code-block:: bash

    conda install -c conda-forge pyxel-sim jupyterlab
    python -m pip install lacosmic


To leave the environment, you may activate another one or just type:

.. code-block:: bash

    conda activate

If you want to remove a conda environment, you can use the following command:

.. code-block:: bash

    conda env remove -n my-pyxel-analysis


..
    Full installation
    -----------------

    And finally **you can install Pyxel** (in the current conda environment)

    .. code-block:: bash

        conda install -c conda-forge pyxel-sim

    For now, it's not possible to install
    `lacosmic <https://lacosmic.readthedocs.io/en/stable/api/lacosmic.lacosmic.html#lacosmic.lacosmic>`__
    from ``conda``.
    The user **must** install ``lacosmic`` manually (in the current conda environment) with the command ``pip``:

    .. code-block:: bash

        conda install -c conda-forge pyxel-sim
        pip install lacosmic


    .. warning::
        Conda 64-bit **must** be installed and not Conda 32-bit.


    It is recommended to also install JupyterLab (for example).
    In this case you must run the command:

    .. code-block:: bash

        conda install -c conda-forge jupyterlab


    You can also install Pyxel and JupyterLab at the same time (recommended):

    .. code-block:: bash

        conda install -c conda-forge pyxel-sim jupyterlab


    Updating
    --------

    To update Pyxel with ``conda``, you can use the following command:

    .. code-block:: bash

       conda update pyxel-sim

.. _venv_envs:

Venv Environments
=================

You may prefer to create your virtual environments with Python `venv <https://docs.python.org/3/library/venv.html>`_
command instead of Anaconda.

See `this guide <https://dev.to/bowmanjd/python-tools-for-managing-virtual-environments-3bko#howto>`_
for details on using virtual environments.

To create a virtual environment with ``venv`` in a new ``my-pyxel-analysis`` folder
run the command:

.. code-block:: bash

   python -m venv my-pyxel-analysis

To activate it:

.. tab:: Windows

    .. code-block:: bash

        my-pyxel-analysis\scripts\activate

.. tab:: Linux and MacOS

    .. code-block:: bash

        source ./my-pyxel-analysis/bin/activate

After that you can install pyxel using ``pip`` as well as other packages you may need:


.. code-block:: bash

    python -m pip install pyxel-sim jupyterlab


To leave the environment, you may activate another one or just type:

.. code-block:: bash

    deactivate


..
    When using pip, it's good practice to use a virtual environment.
    See `this guide <https://dev.to/bowmanjd/python-tools-for-managing-virtual-environments-3bko#howto>`_
    for details on using virtual environments.

    First create a new Python virtual environment in the folder `.venv`
    with module `venv <https://docs.python.org/3/library/venv.html>`_

    .. code-block:: bash

       python -m venv .venv


    Then activate this new virtual environment from folder `.venv` before to install Pyxel.

    .. tab:: Windows

        .. code-block:: bash

           # Activate virtual environment '.venv' on Windows
           .venv\scripts\activate

    .. tab:: Linux and MacOS

        .. code-block:: bash

           # Activate virtual environment '.venv' on Linux or MacOS
           source .venv\bin\activate



    .. code-block:: bash

       python -m pip install pyxel-sim

    This will install Pyxel with the required dependencies only.

    To install Pyxel with all optional dependencies, you can specify:

    .. code-block:: bash

        python -m pip install pyxel-sim[all]

    To update an existing installation you can use

    .. code-block:: bash

        python -m pip install pyxel-sim --upgrade

    To install the current Pyxel **development** version using ``pip`` you can use:

    .. code-block:: bash

        python -m pip install git+https://gitlab.com/esa/pyxel.git#egg=pyxel-sim

    Or like this, if you want to study or edit the code locally:

    .. code-block:: bash

        git clone https://gitlab.com/esa/pyxel.git
        cd pyxel
        python -m pip install .


    .. note::
        The libraries ``pygmo2`` and ``lacosmic`` are not installed with these
        compulsory requirements.

        ``pygmo2`` is needed for the calibration mode.
        ``lacosmic`` is needed for 'remove_cosmic_rays' model.

    It is recommended to also install JupyterLab (for example).
    In this case you must run the command:

    .. code-block:: bash

        pip install jupyterlab


    You can also install Pyxel and JupyterLab at the same time (recommended):

    .. code-block:: bash

        pip install pyxel-sim jupyterlab
