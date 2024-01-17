.. _MKID architecture:

####
MKID
####

As reported in :cite:p:`2020:prodhomme`,
a superconducting microwave kinetic-inductance detector (MKID) is a novel concept of photo-detector
tailored for wavelengths below a few millimetres :cite:p:`doi:10.1146/annurev-conmatphys-020911-125022`.
Essentially, it is an LC micro-resonator with a superconducting photo-sensitive area,
which is capable of detecting single photons; as well as providing a measurement on their arrival time and energy.
Operationally, each photon impinging on the MKID breaks a number of superconducting charge carriers,
called Cooper pairs, into quasi-particles.
In turn, thanks to the principle of kinetic inductance,
which becomes relevant only below a superconducting critical temperature,
such a strike is converted into a sequence of microwave pulses (at a few $GHz$) with a wavelength-dependent profile;
which are then read out one by one, on a single channel.
An important caveat is that the photo-generated pulse profiles can be distinguished only if they do not overlap in time
and if the read-out bandwidth is large enough.
The situation is analogous to the "pulse pile-up" and "coincidence losses" of EM-CCDs,
in photon-counting mode [e.g., Wilkins et al., 2014]. In other words,
there is a maximum limit to the achievable count rate,
which is inversely proportional to the minimum distance in time between distinguishable pulse profiles:
the so-called "dead time",
which is fundamentally determined by the recombination time of quasi-particles re-forming Cooper pairs.
Given this, an MKID-array per se can serve as an intrinsic integral-field spectrograph,
at low resolution, without any dispersive elements or chromatic filters :cite:p:`Mazin`.

API reference: :py:class:`~pyxel.detectors.MKID`

Available models
================

* Scene generation
    * :ref:`scene_generation_create_store_detector`
    * :ref:`load_star_map`
* Photon collection
    * :ref:`photon_collection_create_store_detector`
    * :ref:`aperture`
    * :ref:`Load image`
    * :ref:`Simple illumination`
    * :ref:`Stripe pattern`
    * :ref:`Shot noise`
    * :ref:`Physical Optics Propagation in PYthon (POPPY)`
    * :ref:`Load PSF`
* Charge generation
    * :ref:`charge_generation_create_store_detector`
    * :ref:`Simple photoconversion`
    * :ref:`Conversion with custom QE map`
    * :ref:`Load charge`
    * :ref:`CosmiX cosmic ray model`
    * :ref:`Dark current`
    * :ref:`Simple dark current`
* Phasing
    * :ref:`phasing_create_store_detector`
    * :ref:`Pulse processing`
* Charge collection
    * :ref:`charge_collection_create_store_detector`
    * :ref:`Simple collection`
    * :ref:`Simple full well`
    * :ref:`Fixed pattern noise`
* Charge measurement:
    * :ref:`charge_measurement_create_store_detector`
    * :ref:`DC offset`
    * :ref:`kTC reset noise`
    * :ref:`Simple charge measurement`
    * :ref:`Output node noise`
    * :ref:`Non-linearity (polynomial)`
* Readout electronics:
    * :ref:`readout_electronics_create_store_detector`
    * :ref:`Simple ADC`
    * :ref:`Simple amplification`
    * :ref:`Dead time filter`
    * :ref:`Simple phase conversion`
* Data processing:
    * :ref:`data_processing_create_store_detector`
    * :ref:`statistics`
    * :ref:`mean_variance`
    * :ref:`linear_regression`
    * :ref:`extract_roi_to_xarray`
    * :ref:`remove_cosmic_rays`
    * :ref:`snr`
