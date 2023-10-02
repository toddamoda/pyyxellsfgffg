.. _APD architecture:

###
APD
###

API reference: :py:class:`~pyxel.detectors.APD`

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
    * :ref:`APD gain`
    * :ref:`Dark current Saphira`
* Charge collection
    * :ref:`charge_collection_create_store_detector`
    * :ref:`Simple collection`
    * :ref:`Simple full well`
    * :ref:`Fixed pattern noise`
* Charge measurement:
    * :ref:`charge_measurement_create_store_detector`
    * :ref:`DC offset`
    * :ref:`Output pixel reset voltage APD`
    * :ref:`kTC reset noise`
    * :ref:`Simple charge measurement`
    * :ref:`Readout noise Saphira`
    * :ref:`Non-linearity (polynomial)`
* Readout electronics:
    * :ref:`readout_electronics_create_store_detector`
    * :ref:`Simple ADC`
* Data processing:
    * :ref:`data_processing_create_store_detector`
    * :ref:`statistics`
    * :ref:`linear_regression`
    * :ref:`mean_variance`
    * :ref:`extract_roi_to_xarray`
    * :ref:`remove_cosmic_rays`
    * :ref:`snr`
