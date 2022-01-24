.. _phasing:

==============
Phasing models
==============

.. currentmodule:: pyxel.models.phasing

Phasing models deal with the photo-generated phase pulses in the input probe signal of an MKID-array; i.e. with a :py:class:`~pyxel.data_structure.Phase` array, inside the :py:class:`~pyxel.detectors.Detector` object. Essentially, the starting point of each phase pulse indicates the arrival time of the photon that generated it---assuming that the pulse itself does not overlap with other pulses. Moreover, the height of the pulse provides information about the photon's energy---actually, fitting the pulse’s profile is a more robust approximation. The initial :py:class:`~pyxel.data_structure.Phase` array builds upon a :py:class:`~pyxel.data_structure.Charge` array tailored for superconducting photo-detectors---once their underlying physics is fully implemented.

More information can be found on the website :cite:p:`Mazin`.

Pulse processing
================

:guilabel:`Charge` 🠆 :guilabel:`Phase`

This model only applies to the :py:class:`~pyxel.detectors.MKID` detector.

When a photon impinges upon an MKID, it generates a phase pulse in its input probe signal :math:`\phi = \frac{\lambda}{r}`; where :math:`\phi` is the mean phase height, :math:`\lambda` the wavelength associated with the photon and *r* the responsivity.

This model is derived from :cite:p:`Dodkins`; more information can be found on the website :cite:p:`Mazin`.

Example of YAML configuration model:

.. code-block:: yaml

    - name: pulse_processing
      func: pyxel.models.phasing.pulse_processing
      enabled: true
      arguments:
        wavelength:
        responsivity:
        scaling_factor: #

.. note:: This model is specific to the :term:`MKID` detector.

.. autofunction:: pulse_processing
