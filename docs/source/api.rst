Package API
===========


..
  UML from file location
  .. uml:: _static/example.puml

Detector classes
----------------

Detector classes and their attributes.

.. autoclass:: pyxel.detectors.ccd_geometry.CCDGeometry
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members:

.. autoclass:: pyxel.detectors.cmos_geometry.CMOSGeometry
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pyxel.detectors.ccd_characteristics.CCDCharacteristics
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pyxel.detectors.cmos_characteristics.CMOSCharacteristics
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pyxel.detectors.material.Material
    :members:
    :undoc-members:

.. autoclass:: pyxel.detectors.environment.Environment
    :members:
    :undoc-members:

.. autoclass:: pyxel.detectors.optics.Optics
    :members:
    :undoc-members:


Models
------


Photon Generation models
************************

.. automodule:: pyxel.models.photon_generation
    :members:
    :undoc-members:
    :imported-members:

.. autofunction:: pyxel.models.photon_generation.add_photons.add_photons(param1 = None, param2)

.. autofunction:: pyxel.models.photon_generation.load_image.load_image(param1, param2: int = 0)

.. autofunction:: pyxel.models.photon_generation.shot_noise.add_shot_noise(param1, param2)

Optical models
**************

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

