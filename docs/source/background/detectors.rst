.. _detectors:

#########
Detectors
#########

According to the ``YAML`` file, one :py:class:`~pyxel.detectors.CCD` or
:py:class:`~pyxel.detectors.CMOS` :py:class:`~pyxel.detectors.Detector` object is
instantiated for each thread, inheriting from a general (abstract)
:py:class:`~pyxel.detectors.Detector` class.

The created :py:class:`~pyxel.detectors.Detector` object is the input of the
Detection :ref:`pipelines`, which is passed through all the including models
represented by functions. We can consider the :py:class:`~pyxel.detectors.Detector`
object as a bucket containing all information and data related to the physical
properties of the simulated detector (:py:class:`~pyxel.detectors.Geometry`,
:py:class:`~pyxel.detectors.Material`, :py:class:`~pyxel.detectors.Environment`,
:py:class:`~pyxel.detectors.Characteristics`), incident photons, created charge-carriers
and the generated signals we are interested in at the end of the simulation.

.. figure:: _static/pyxel_detector.png
    :scale: 25%
    :alt: detector
    :align: center

.. _data_structure:

CCD
===

CMOS
====

MKID
====

As reported in :cite:p:`2020:prodhomme`, a superconducting microwave kinetic-inductance detector (MKID) is a novel concept of photo-detector tailored for wavelengths below a few millimetres :cite:p:`doi:10.1146/annurev-conmatphys-020911-125022`. Essentially, it is an LC micro-resonator with a superconducting photo-sensitive area, which is capable of detecting single photons; as well as providing a measurement on their arrival time and energy. Operationally, each photon impinging on the MKID breaks a number of superconducting charge carriers, called Cooper pairs, into quasi-particles. In turn, thanks to the principle of kinetic inductance---which becomes relevant only below a superconducting critical temperature---such a strike is converted into a sequence of microwave pulses (at a few *GHz*) with a wavelength-dependent profile; which are then read out one by one, on a single channel. An important caveat is that the photo-generated pulse profiles can be distinguished only if they do not overlap in time and if the read-out bandwidth is large enough. The situation is analogous to the "pulse pile-up" and "coincidence losses" of EM-CCDs, in photon-counting mode [e.g., Wilkins et al., 2014]. In other words, there is a maximum limit to the achievable count rate, which is inversely proportional to the minimum distance in time between distinguishable pulse profiles: the so-called "dead time", which is fundamentally determined by the recombination time of quasi-particles re-forming Cooper pairs. Given this, an MKID-array per se can serve as an intrinsic integral-field spectrograph, at low resolution, without any dispersive elements or chromatic filters :cite:p:`Mazin`.

Data Structure
==============

Models in Pyxel should be able to add photons, charges, charge packets, signal [#]_ or
image pixel values to the corresponding data structure classes
(:py:class:`~pyxel.data_structure.Photon`, :py:class:`~pyxel.data_structure.Charge`,
:py:class:`~pyxel.data_structure.Pixel`, :py:class:`~pyxel.data_structure.Signal`
or :py:class:`~pyxel.data_structure.Image` class).
These classes are storing the data values either inside a Pandas
:py:class:`pandas.DataFrame` or in a NumPy :py:class:`numpy.ndarray`. Via DataFrame or
NumPy array handling functions, models can also modify properties of photons,
charges, etc., like position, kinetic energy, number of electrons per charge packet,
signal amplitude, etc.

.. [#] Which is going to be a :py:class:`~pyxel.data_structure.Phase`, in the case of MKIDs---once their underlying physics is fully implemented.
