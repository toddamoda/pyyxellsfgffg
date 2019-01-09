.. _models:

Models
===========

By models, we mean various analytical functions, numerical methods or
algorithms implemented in order to approximate, calculate, visualize
electro-optical performance and degradation due to the operational environment
(space, laboratory test) and its effects (e.g. radiation damage).

Models can be grouped into 7 model levels per detector type according to
which object or parameter of the Detector object is used or modified by
the models. These levels correspond roughly to the detector fundamental
functions. Models in Pyxel should be able to add photons, charge,
charge packets or signal values to the corresponding objects (Photon,
Charge, Pixel, Signal or Image object), which are storing the physics data
either inside a Pandas dataframe or in a NumPy array. Via dataframe or
array handling functions, models can also modify properties of photons,
charge, etc. within these objects, like wavelength, position, kinetic
energy, number of electrons per charge packet, signal amplitude, etc.
Models could also modify any detector parameters (like quantum efficiency,
gain, standard deviation of noises) globally on detector level or locally
(on pixel level or for a specific detector area).

.. figure:: _static/model-table.PNG
    :scale: 70%
    :alt: models
    :align: center

    All the 8 model levels, which are imitating the physical working principles of imaging detectors. They were
    grouped according to which physics data storing objects are modified by them. Note that 2 out of the 8 levels are
    specific to a single detector type.


Photon Generation models
---------------------------------

.. automodule:: pyxel.models.photon_generation
    :members:
    :undoc-members:
    :imported-members:

.. autofunction:: pyxel.models.photon_generation.add_photons.add_photons(param1 = None, param2)
.. autofunction:: pyxel.models.photon_generation.load_image.load_image(param1, param2: int = 0)
.. autofunction:: pyxel.models.photon_generation.shot_noise.add_shot_noise(param1, param2)

Optical models
---------------------------------

.. automodule:: pyxel.models.optics
    :members:
    :undoc-members:
    :imported-members:

Charge Generation models
---------------------------------

.. automodule:: pyxel.models.charge_generation
    :members:
    :undoc-members:
    :imported-members:

.. autofunction:: pyxel.models.charge_generation.tars.tars.run_tars
.. autofunction:: pyxel.models.charge_generation.charge_injection.charge_injection
.. autofunction:: pyxel.models.charge_generation.photoelectrons.simple_conversion

Charge Collection models
---------------------------------

.. automodule:: pyxel.models.charge_collection
    :members:
    :undoc-members:
    :imported-members:

.. autofunction:: pyxel.models.charge_collection.collection.simple_collection
.. autofunction:: pyxel.models.charge_collection.fix_pattern_noise.add_fix_pattern_noise
.. autofunction:: pyxel.models.charge_collection.full_well.simple_pixel_full_well

Charge Transfer models (CCD)
---------------------------------

Only for CCD detectors.

.. automodule:: pyxel.models.charge_transfer
    :members:
    :undoc-members:
    :imported-members:

.. autofunction:: pyxel.models.charge_transfer.cdm.CDM.cdm

Charge Measurement models
---------------------------------

.. automodule:: pyxel.models.charge_measurement
    :members:
    :undoc-members:
    :imported-members:

.. autofunction:: pyxel.models.charge_measurement.measurement.simple_measurement
.. autofunction:: pyxel.models.charge_measurement.readout_noise.output_node_noise

Signal Transfer models (CMOS)
---------------------------------

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
---------------------------------

.. automodule:: pyxel.models.readout_electronics
    :members:
    :undoc-members:
    :imported-members:

.. autofunction:: pyxel.models.readout_electronics.digitization.simple_digitization
