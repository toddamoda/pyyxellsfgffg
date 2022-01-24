.. _phasing:

==============
Phasing models
==============

.. currentmodule:: pyxel.models.phasing

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
