.. _CMOS architecture:

####
CMOS
####

API reference: :py:class:`~pyxel.detectors.CMOS`

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
    * :ref:`Wavelength dependence AIRS`
* Charge generation
    * :ref:`charge_generation_create_store_detector`
    * :ref:`Simple photoconversion`
    * :ref:`Conversion with custom QE map`
    * :ref:`Load charge`
    * :ref:`CosmiX cosmic ray model`
    * :ref:`Dark current rule07`
    * :ref:`Dark current`
    * :ref:`Simple dark current`
    * :ref:`Dark current induced`
* Charge collection
    * :ref:`charge_collection_create_store_detector`
    * :ref:`Simple collection`
    * :ref:`Simple full well`
    * :ref:`Fixed pattern noise`
    * :ref:`Inter pixel capacitance`
    * :ref:`Simple persistence`
    * :ref:`Persistence`
* Charge measurement:
    * :ref:`charge_measurement_create_store_detector`
    * :ref:`DC offset`
    * :ref:`kTC reset noise`
    * :ref:`Simple charge measurement`
    * :ref:`Output node noise CMOS`
    * :ref:`Non-linearity (polynomial)`
    * :ref:`Simple physical non-linearity`
    * :ref:`Physical non-linearity`
    * :ref:`Physical non-linearity with saturation`
    * :ref:`HxRG noise generator`
* Readout electronics:
    * :ref:`readout_electronics_create_store_detector`
    * :ref:`Simple ADC`
    * :ref:`Simple amplification`
    * :ref:`DC crosstalk`
    * :ref:`AC crosstalk`
    * :ref:`SAR ADC`
* Data processing:
    * :ref:`data_processing_create_store_detector`
    * :ref:`statistics`
    * :ref:`mean_variance`
    * :ref:`linear_regression`
    * :ref:`extract_roi_to_xarray`
    * :ref:`remove_cosmic_rays`
    * :ref:`snr`
