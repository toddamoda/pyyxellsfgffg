.. _phasing:

==============
Phasing models
==============

.. currentmodule:: pyxel.models.phasing

Phasing models deal with the photo-generated phase pulses in the input probe signal of an MKID-array; i.e. with a
:py:class:`~pyxel.data_structure.Phase` array, inside the :py:class:`~pyxel.detectors.Detector` object. Essentially,
the starting point of each phase pulse indicates the arrival time of the photon that generated it---assuming that the
pulse itself does not overlap with other pulses. Moreover, the height of the pulse provides information about the
photon's energy---actually, fitting the pulse’s profile is a more robust approximation. The initial
:py:class:`~pyxel.data_structure.Phase` array builds upon a :py:class:`~pyxel.data_structure.Charge` array tailored for
superconducting photo-detectors---once their underlying physics is fully implemented.

More information can be found on the website :cite:p:`Mazin`.

.. _phasing_create_store_detector:

Create and Store a detector
===========================

The models :ref:`phasing_save_detector` and :ref:`phasing_load_detector`
can be used respectively to create and to store a :py:class:`~pyxel.detectors.Detector` to/from a file.

These models can be used when you want to store or to inject a :py:class:`~pyxel.detectors.Detector`
into the current :ref:`pipeline`.

.. _phasing_save_detector:

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


.. _phasing_load_detector:

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



.. _Pulse processing:

Pulse processing
================

:guilabel:`Charge` → :guilabel:`Phase`

This model only applies to the :py:class:`~pyxel.detectors.MKID` detector.

When a photon impinges upon an MKID, it generates a phase pulse in its input probe signal, on top of the background
phase-height noise (from two-level-system states and amplifier noise). Each MKID has a phase-height responsivity
:math:`r = \frac{\lambda}{\phi}`; where :math:`\lambda` is the wavelength associated with the photons under study and
:math:`\phi` is the mean phase height.

This model is derived from :cite:p:`Dodkins`; more information can be found on the website :cite:p:`Mazin`.

Example of YAML configuration model:

.. code-block:: yaml

    - name: pulse_processing
      func: pyxel.models.phasing.pulse_processing
      enabled: true
      arguments:
        wavelength:
        responsivity:
        scaling_factor: 2.5e2

.. note:: This model is specific for the :term:`MKID` detector.

.. autofunction:: pulse_processing