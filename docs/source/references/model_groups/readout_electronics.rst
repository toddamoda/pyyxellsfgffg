.. _readout_electronics:

==========================
Readout Electronics models
==========================

.. currentmodule:: pyxel.models.readout_electronics

Readout electronics models are used to add TBW.

.. _readout_electronics_create_store_detector:

Create and Store a detector
===========================

The models :ref:`readout_electronics_save_detector` and :ref:`readout_electronics_load_detector`
can be used respectively to create and to store a :py:class:`~pyxel.detectors.Detector` to/from a file.

These models can be used when you want to store or to inject a :py:class:`~pyxel.detectors.Detector`
into the current :ref:`pipeline`.

.. _readout_electronics_save_detector:

Save detector
-------------

This model saves the current :py:class:`~pyxel.detectors.Detector` into a file.
Accepted file formats are ``.h5``, ``.hdf5``, ``.hdf`` and ``.asdf``.

.. code-block:: yaml

    - name: save_detector
      func: pyxel.models.save_detector
      enabled: true
      arguments:
        filename: my_detector.h5

.. autofunction:: pyxel.models.save_detector
   :noindex:


.. _readout_electronics_load_detector:

Load detector
-------------

This model loads a :py:class:`~pyxel.detectors.Detector` from a file and injects it in the current pipeline.
Accepted file formats are ``.h5``, ``.hdf5``, ``.hdf`` and ``.asdf``.

.. code-block:: yaml

    - name: load_detector
      func: pyxel.models.load_detector
      enabled: true
      arguments:
        filename: my_detector.h5

.. autofunction:: pyxel.models.load_detector
   :noindex:


.. _Simple ADC:

Simple ADC
==========

:guilabel:`Signal` → :guilabel:`Image`

With this model you can convert :py:class:`~pyxel.data_structure.Signal`
array into :py:class:`~pyxel.data_structure.Image` mimicking an ideal Analog to Digital Converter (ADC).
The parameters ``adc_bit_resolution`` and ``adc_voltage_range`` from detector
:py:class:`~pyxel.detectors.Characteristics` are used.
Output data_type can also be specified with the parameter ``data_type``.
If not provided, data_type is determined based on ``detector.characteristics.adc_bit_resolution``.

Example of the configuration file:

.. code-block:: yaml

    - name: simple_adc
      func: pyxel.models.readout_electronics.simple_adc
      enabled: true
      arguments:
        data_type: uint32   # optional

.. autofunction:: simple_adc

.. _Simple amplification:

Simple amplification
====================

:guilabel:`Signal` → :guilabel:`Signal`

Amplify signal using gain from the output amplifier (in V/V) and
the signal processor (in V/V).


Example of the configuration file:

.. code-block:: yaml

    - name: simple_amplifier
      func: pyxel.models.readout_electronics.simple_amplifier
      enabled: true

.. autofunction:: simple_amplifier

.. _DC crosstalk:

DC crosstalk
============

:guilabel:`Signal` → :guilabel:`Signal`

Apply DC crosstalk signal to detector signal.

Example of the configuration file:

.. code-block:: yaml

    - name: dc_crosstalk
      func: pyxel.models.readout_electronics.dc_crosstalk
      enabled: true
      arguments:
        coupling_matrix: [[1, 0.5, 0, 0], [0.5, 1, 0, 0], [0, 0, 1, 0.5], [0, 0, 0.5, 1]]
        channel_matrix: [1,2,3,4]
        readout_directions: [1,2,1,2]

.. autofunction:: dc_crosstalk

.. _AC crosstalk:

AC crosstalk
============

:guilabel:`Signal` → :guilabel:`Signal`

Apply AC crosstalk signal to detector signal.

Example of the configuration file:

.. code-block:: yaml

    - name: ac_crosstalk
      func: pyxel.models.readout_electronics.ac_crosstalk
      enabled: true
      arguments:
        coupling_matrix: [[1, 0.5, 0, 0], [0.5, 1, 0, 0], [0, 0, 1, 0.5], [0, 0, 0.5, 1]]
        channel_matrix: [1,2,3,4]
        readout_directions: [1,2,1,2]

.. autofunction:: ac_crosstalk

.. _Dead time filter:

Dead time filter
================

:guilabel:`Phase` → :guilabel:`Phase`

This model only applies to the :py:class:`~pyxel.detectors.MKID` detector.

There is a maximum limit to the achievable count rate, which is inversely proportional to the minimum distance in time between distinguishable pulse profiles: the so-called “dead time”, which is fundamentally determined by the recombination time of quasi-particles re-forming Cooper pairs :cite:p:`2020:prodhomme`.

The underlying physics of this model is described in :cite:p:`PhysRevB.104.L180506`; more information can be found on the website :cite:p:`Mazin`.

Example of the configuration file:

.. code-block:: yaml

    - name: dead_time_filter
      func: pyxel.models.readout_electronics.dead_time_filter
      enabled: true
      arguments:
        tau_0: 4.4e-7
        n_0: 1.72e10
        t_c: 1.26
        v: 30.0
        t_op: 0.3
        tau_pb: 2.8e-10
        tau_esc: 1.4e-10
        tau_sat: 1.0e-3

.. note:: This model is specific to the :term:`MKID` detector.

.. autofunction:: dead_time_filter

.. _SAR ADC:

SAR ADC
=======

:guilabel:`Signal` → :guilabel:`Image`

Digitize signal array using SAR (Successive Approximation Register) :term:`ADC` logic.
The parameters ``adc_bit_resolution`` and ``adc_voltage_range`` from detector
:py:class:`~pyxel.detectors.Characteristics` are used.

Example of the configuration file:

.. code-block:: yaml

    - name: sar_adc
      func: pyxel.models.readout_electronics.sar_adc
      enabled: true

.. autofunction:: sar_adc

.. _SAR ADC with noise:

SAR ADC with noise
==================

:guilabel:`Signal` → :guilabel:`Image`

Digitize signal array using :term:`SAR` (Successive Approximation Register) :term:`ADC`
logic with noise.
The parameters ``adc_bit_resolution`` and ``adc_voltage_range`` from detector
:py:class:`~pyxel.detectors.Characteristics` are used.

Example of the configuration file for ``adc_bit_resolution`` equals to 8 bits:

.. code-block:: yaml

    - name: sar_adc_with_noise
      func: pyxel.models.readout_electronics.sar_adc_with_noise
      strengths: [0., 0., 0., 0., 0.1, 0.2, 0.3, 0.1]
      noises: [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
      enabled: true

.. autofunction:: sar_adc_with_noise

.. _Simple phase conversion:

Simple phase conversion
=======================

:guilabel:`Phase` → :guilabel:`Image`

With this model you can convert :py:class:`~pyxel.data_structure.Phase`
array into :py:class:`~pyxel.data_structure.Image`, given a hard-coded multiplicative conversion factor.

Example of the configuration file:

.. code-block:: yaml

    - name: simple_phase_conversion
      func: pyxel.models.readout_electronics.simple_phase_conversion
      enabled: true

.. note:: This model is specific to the :term:`MKID` detector.

.. autofunction:: simple_phase_conversion
