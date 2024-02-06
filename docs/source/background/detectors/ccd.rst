.. _CCD architecture:

===
CCD
===
API reference: :py:class:`~pyxel.detectors.CCD`

As reported in :cite:p:`2001:janesick`, a Charge-Coupled Device (CCD) detector is a vital component in modern imaging technology, proficient in capturing light across a wide spectrum.
Operating on the principle of converting incident photons into electrical charge, CCDs offer exceptional sensitivity, capable of detecting individual photons with precision.
This sensitivity makes CCDs invaluable in various scientific and industrial applications, including astronomy, microscopy, and digital photography.

Despite their versatility, CCDs face challenges such as thermal noise and dark current, which can affect image quality.
Nevertheless, ongoing advancements in sensor technology and signal processing continue to enhance the performance and utility of CCD detectors, ensuring their continued importance in scientific research and visual documentation.

Below all available models for CCD are listed.

.. _CCD models:

Available models
----------------

* Scene generation
    * :ref:`scene_generation_create_store_detector`
    * :ref:`load_star_map`
* Photon collection
    * :ref:`photon_collection_create_store_detector`
    * :ref:`simple_collection`
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
    * :ref:`Conversion with 3D QE map`
    * :ref:`Apply QE curve`
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
    * :ref:`EMCCD Model`
    * :ref:`EMCCD Clock Induced Charge (CIC)`
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
* Data processing:
    * :ref:`data_processing_create_store_detector`
    * :ref:`statistics`
    * :ref:`mean_variance`
    * :ref:`linear_regression`
    * :ref:`extract_roi_to_xarray`
    * :ref:`remove_cosmic_rays`
    * :ref:`snr`
