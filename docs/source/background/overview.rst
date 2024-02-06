.. _background:

Overview
========

The section  **Background/Explanations** provides information on key concepts behind Pyxel,
covering topics such as Pyxel's :ref:`architecture <architecture>`,
:ref:`input configuration files <yaml>` and the :ref:`running modes <running_modes>`.
Use this section if you want to learn more about how Pyxel works
and what different :ref:`running modes <running_modes>` can be used for.

Further information on specific parts of the code can be found in the :ref:`Reference<reference>` section.



.. grid:: 1 2 2 2
    :gutter: 4

    .. grid-item-card::
        :text-align: center

        **Architecture**
        ^^^

        Pyxel's architecture comprises running modes,
        and the pipeline, defined in configuration files.

        Detectors store properties and data used by models in
        the pipeline <pipeline>, mimicking detector principles.
        
        +++

        .. button-ref:: architecture
            :ref-type: ref
            :click-parent:
            :color: primary
            :outline:
            :expand:

            More explanations

    .. grid-item-card::
        :text-align: center

        **Pixel Coordinate Conventions**
        ^^^

        Define the convention used for the coordinates in Pyxel.

        +++

        .. button-ref:: pixel_coordinate_conventions
            :ref-type: ref
            :click-parent:
            :color: primary
            :outline:
            :expand:

            More explanations

    .. grid-item-card::
        :text-align: center

        **Detectors**
        ^^^

        The Detector object in Pyxel's pipeline holds
        data crucial for model execution,
        including physical properties like geometry, characteristics,
        and environment, defined in the YAML configuration file.

        +++

        .. button-ref:: detectors
            :ref-type: ref
            :click-parent:
            :color: primary
            :outline:
            :expand:

            More explanations


    .. grid-item-card::
        :text-align: center

        **Pipelines**
        ^^^

        The Detection pipeline, represented by the DetectionPipeline class,
        hosts various models grouped into levels resembling
        detector principles, with user-customizable order.

        +++

        .. button-ref:: pipeline
            :ref-type: ref
            :click-parent:
            :color: primary
            :outline:
            :expand:

            More explanations

    .. grid-item-card::
        :text-align: center

        **Configuration file**
        ^^^

        A configuration file is the main user entry point for any Pyxel simulation.

        Pyxel utilizes YAML configuration files to define
        running modes, detectors properties, and effect models.

        These files are user-friendly but can be validated using JSON Schema
        for error prevention.
        +++

        .. button-ref:: yaml
            :ref-type: ref
            :click-parent:
            :color: primary
            :outline:
            :expand:

            More explanations

    .. grid-item-card::
        :text-align: center

        **Running modes**
        ^^^

        Pyxel offers three running modes: Exposure mode for single or incremental exposures,
        Observation mode for multiple exposures over a range of parameters
        and Calibration mode for model fitting/optimization.

        +++

        .. button-ref:: running_modes
            :ref-type: ref
            :click-parent:
            :color: primary
            :outline:
            :expand:

            More explanations
