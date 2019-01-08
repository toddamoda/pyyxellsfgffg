Package API
===========


..
  UML from file location
  .. uml:: _static/example.puml

Detectors
-----------

Detector classes and their attributes.

Geometry
***********

.. autoclass:: pyxel.detectors.ccd_geometry.CCDGeometry
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members:

.. autoclass:: pyxel.detectors.cmos_geometry.CMOSGeometry
    :members:
    :undoc-members:
    :show-inheritance:


Characteristics
*****************

.. autoclass:: pyxel.detectors.ccd_characteristics.CCDCharacteristics
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pyxel.detectors.cmos_characteristics.CMOSCharacteristics
    :members:
    :undoc-members:
    :show-inheritance:


Material
***********

.. autoclass:: pyxel.detectors.material.Material
    :members:
    :undoc-members:


Environment
***********

.. autoclass:: pyxel.detectors.environment.Environment
    :members:
    :undoc-members:


Optics
***********

.. autoclass:: pyxel.detectors.optics.Optics
    :members:
    :undoc-members:


Models
------

Photon Generation models
*********************************

.. automodule:: pyxel.models.photon_generation
    :members:
    :undoc-members:
    :imported-members:

.. autofunction:: pyxel.models.photon_generation.add_photons.add_photons(param1 = None, param2)
.. autofunction:: pyxel.models.photon_generation.load_image.load_image(param1, param2: int = 0)
.. autofunction:: pyxel.models.photon_generation.shot_noise.add_shot_noise(param1, param2)

Optical models
*********************************

.. automodule:: pyxel.models.optics
    :members:
    :undoc-members:
    :imported-members:

Charge Generation models
*********************************

.. automodule:: pyxel.models.charge_generation
    :members:
    :undoc-members:
    :imported-members:

.. autofunction:: pyxel.models.charge_generation.tars.tars.run_tars
.. autofunction:: pyxel.models.charge_generation.charge_injection.charge_injection
.. autofunction:: pyxel.models.charge_generation.photoelectrons.simple_conversion

Charge Collection models
*********************************

.. automodule:: pyxel.models.charge_collection
    :members:
    :undoc-members:
    :imported-members:

.. autofunction:: pyxel.models.charge_collection.collection.simple_collection
.. autofunction:: pyxel.models.charge_collection.fix_pattern_noise.add_fix_pattern_noise
.. autofunction:: pyxel.models.charge_collection.full_well.simple_pixel_full_well

Charge Transfer models (CCD)
*********************************

Only for CCD detectors.

.. automodule:: pyxel.models.charge_transfer
    :members:
    :undoc-members:
    :imported-members:

.. autofunction:: pyxel.models.charge_transfer.cdm.CDM.cdm

Charge Measurement models
*********************************

.. automodule:: pyxel.models.charge_measurement
    :members:
    :undoc-members:
    :imported-members:

.. autofunction:: pyxel.models.charge_measurement.measurement.simple_measurement
.. autofunction:: pyxel.models.charge_measurement.readout_noise.output_node_noise

Signal Transfer models (CMOS)
*********************************

Only for CMOS-based detectors.

.. automodule:: pyxel.models.signal_transfer
    :members:
    :undoc-members:
    :imported-members:

.. autofunction:: pyxel.models.signal_transfer.nghxrg.nghxrg.ktc_bias_noise
.. autofunction:: pyxel.models.signal_transfer.nghxrg.nghxrg.white_read_noise
.. autofunction:: pyxel.models.signal_transfer.nghxrg.nghxrg.acn_noise
.. autofunction:: pyxel.models.signal_transfer.nghxrg.nghxrg.uncorr_pink_noise
.. autofunction:: pyxel.models.signal_transfer.nghxrg.nghxrg.corr_pink_noise
.. autofunction:: pyxel.models.signal_transfer.nghxrg.nghxrg.pca_zero_noise

Readout Electronics models
*********************************

.. automodule:: pyxel.models.readout_electronics
    :members:
    :undoc-members:
    :imported-members:

.. autofunction:: pyxel.models.readout_electronics.digitization.simple_digitization
