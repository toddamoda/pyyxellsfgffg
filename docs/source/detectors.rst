.. _detectors:

Detectors
===========

..
  UML from file location
  .. uml:: _static/example.puml

Detector classes and their attributes.


According to the YAML file, one CCD or CMOS Detector object is instantiated
for each thread, inheriting from a general (abstract) Detector class. The
created Detector object is the input of the Detection pipeline, which is
passed through all the including models represented by functions. We can
consider the Detector object as a bucket containing all information and data
related to the physical properties of the simulated detector (geometry,
material, environment, characteristics), incident photons, created
charge-carriers and the generated signals we are interested in at the
end of the simulation.



.. _geometry:

Geometry
-----------

.. autoclass:: pyxel.detectors.ccd_geometry.CCDGeometry
    :members:
    :inherited-members:
    :undoc-members:
    :show-inheritance:
    :exclude-members:

.. autoclass:: pyxel.detectors.cmos_geometry.CMOSGeometry
    :members:
    :inherited-members:
    :undoc-members:
    :show-inheritance:


.. _characteristics:

Characteristics
----------------

.. autoclass:: pyxel.detectors.ccd_characteristics.CCDCharacteristics
    :members:
    :inherited-members:
    :undoc-members:
    :show-inheritance:
    :exclude-members:

.. autoclass:: pyxel.detectors.cmos_characteristics.CMOSCharacteristics
    :members:
    :inherited-members:
    :undoc-members:
    :show-inheritance:
    :exclude-members:

.. _material:

Material
-----------

.. autoclass:: pyxel.detectors.material.Material
    :members:
    :undoc-members:
    :exclude-members:


.. _environment:

Environment
-----------

.. autoclass:: pyxel.detectors.environment.Environment
    :members:
    :undoc-members:
    :exclude-members:


.. _optics:

Optics
-----------

.. autoclass:: pyxel.detectors.optics.Optics
    :members:
    :undoc-members:
    :exclude-members:
