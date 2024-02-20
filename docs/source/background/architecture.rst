.. _architecture:

============
Architecture
============

There are three primary components behind Pyxel's architecture,
the :ref:`running_modes`, the :ref:`detectors` and the :ref:`pipeline`.
Each of these components is represented by a class within the codebase.
For further insight into these components, refer to the :ref:`apireference`.

The primary entry point for any Pyxel simulation is a configuration file, defined before executing Pyxel via
an input YAML configuration file. Additional details regarding configuration files can be found on the :ref:`yaml` page.

As depicted below, the detector encapsulates essential information concerning properties like geometry, characteristics,
and environment conditions. Additionally, it serves as a repository for storing simulated data.
For a comprehensive overview of the data structure, refer to the :ref:`data_structure` page.

This data can be accessed and modified by any model within the pipeline. Serving as the central algorithmic framework,
the pipeline hosts and executes the models, which are categorized into various model groups mirroring the operational
principles of the detector or instrument. Certain models must be enabled in the configuration file to facilitate the
conversion from one data structure to another. These mandatory models are highlighted with an :underline:`underline` in
the accompanying image, while all other models within the pipeline are optional, as they solely manipulate the existing
data repository. For further information, please consult the :ref:`models` page.

Starting from version 2.0, Pyxel has the capability to support multiwavelength models. These models, along with their
respective groups, are visually distinguished by color in the accompanying image. Integration of multiwavelength photons
occurs no later than the charge collection stage, ensuring that they are consolidated across the specified wavelength
range.

.. figure:: _static/architecture.png
    :width: 800px
    :alt: architecture
    :align: center

    :ref:`Detector <detectors>` object and detection :ref:`Pipeline <pipeline>` of Pyxel.
