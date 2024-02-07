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

        Pyxel's architecture comprises :ref:`running modes <running_modes>`,
        :ref:`detectors <detectors>`, and the :ref:`pipeline <pipeline>`,
        defined in :ref:`configuration files <yaml>`.

        Detectors store properties and data used by :ref:`models <models_explanation>` in the :ref:`pipeline <pipeline>`,
        mimicking detector principles.
        
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

        **Configuration file**
        ^^^

        A configuration file is the main user entry point for any Pyxel simulation.

        Pyxel utilizes :ref:`YAML configuration files <yaml>` to define 
        :ref:`running modes <running_modes>`, :ref:`detectors <detectors>` properties,
        and effect models.

        These files are user-friendly but can be validated using :ref:`JSON Schema <json_schema>`
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

        **Detectors**
        ^^^

        Explanations about :ref:`Detector <detectors>` object.

        The :ref:`Detector <detectors>`  object in Pyxel's pipeline holds 
        data crucial for :ref:`model <models_explanation>` execution, 
        including physical :ref:`properties <detector_properties>` like geometry, characteristics, 
        and environment, defined in the :ref:`YAML <yaml>` configuration file.
       
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
        hosts various :ref:`models <models_explanation>` grouped into levels resembling 
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

        **Running modes**
        ^^^

        Pyxel offers three running modes: :ref:`Exposure <exposure_mode>` mode for single or incremental exposures,
        :ref:`Observation <observation_mode>` mode for multiple exposures over a range of parameters
        and :ref:`Calibration <calibration_mode>` mode for model fitting/optimization.

        +++

        .. button-ref:: running_modes
            :ref-type: ref
            :click-parent:
            :color: primary
            :outline:
            :expand:

            More explanations

