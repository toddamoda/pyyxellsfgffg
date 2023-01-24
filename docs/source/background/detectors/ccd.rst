.. _CCD architecture:

###
CCD
###

API reference: :py:class:`~pyxel.detectors.CCD`

Available models
================

* Photon collection
    * :ref:`photon_collection_create_store_detector`
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
    * :ref:`Charge injection`
    * :ref:`CosmiX cosmic ray model`
    * :ref:`Dark current`
    * :ref:`Simple dark current`
* Charge collection
    * :ref:`charge_collection_create_store_detector`
    * :ref:`Simple collection`
    * :ref:`Simple full well`
    * :ref:`Fixed pattern noise`
* Charge transfer
    * :ref:`charge_transfer_create_store_detector`
    * :ref:`Charge Distortion Model (CDM)`
    * :ref:`Add CTI trails (ArCTIc)`
    * :ref:`Remove CTI trails (ArCTIc)`
* Charge measurement:
    * :ref:`charge_measurement_create_store_detector`
    * :ref:`DC offset`
    * :ref:`Simple charge measurement`
    * :ref:`Output node noise`
    * :ref:`Non-linearity (polynomial)`
* Readout electronics:
    * :ref:`readout_electronics_create_store_detector`
    * :ref:`Simple ADC`
    * :ref:`Simple amplification`
    * :ref:`SAR ADC`