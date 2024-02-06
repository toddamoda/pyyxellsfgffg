.. _background:

========
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
    :class-container: sd-text-center

    .. grid-item-card:: Architecture

        The three main elements behind Pyxel's architecture.

        +++

       .. button-ref:: architecture
           :ref-type: ref
           :color: secondary
           :outline:
           :expand:

    .. grid-item-card:: YAML
        :text-align: center

        Configuration file.

       .. button-ref:: yaml
           :ref-type: ref
           :click-parent:
           :color: secondary
           :expand:


    .. grid-item-card:: Detectors
        :text-align: center

        Detector object.

        :doc:`detectors`

    .. grid-item-card:: Pipeline
        :text-align: center

        Core algorithm of the architecture.

        :doc:`pipeline`

    .. grid-item-card:: Running Modes
        :text-align: center

        The three running modes: Exposure, Observation and Calibration modes

        :doc:`running_modes`
