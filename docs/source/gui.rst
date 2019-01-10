.. _gui:

Graphical User Interface
*************************

.. warning::

    The Graphical User Interface (GUI) is not yet operational. Until then
    run Pyxel in batch mode using :ref:`yaml configuration files <yaml>` as input.

The html-based GUI can be opened with any web browser as a webpage to
define or modify input parameters and files, start and monitor the simulation
process or display the images thanks to the integration of JS9 open-source,
JavaScript FITS viewer.

The GUI is automatically generated based on a template YAML configuration
file or any previously saved and loaded YAML file. If a new model has been
added to the framework and YAML file, it is already available and usable
via the GUI.

The GUI communicates with the framework through a Tornado web server, which
allows the user to run the framework remotely on server and use the GUI
only as a local client to start and monitor the progress of the running
simulations.

.. figure:: _static/Pyxel-GUI.png
    :alt: gui
    :align: center

    The Graphical User Interface (GUI) of Pyxel.
