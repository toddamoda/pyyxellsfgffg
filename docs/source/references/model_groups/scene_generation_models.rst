.. _scene_generation:

=======================
Scene Generation models
=======================

.. currentmodule:: pyxel.models.scene_generation

Scene generation models are used to add a scene to :py:class:`~pyxel.data_structure.Scene` data structure
inside the :py:class:`~pyxel.detectors.Detector` object. The values in the :py:class:`~pyxel.data_structure.Scene` array
represent flux per wavelength and area, so number of photons per nanometer per area per second.


.. _scene_generation_create_store_detector:

Create and Store a detector
===========================

The models :ref:`scene_generation_save_detector` and :ref:`scene_generation_load_detector`
can be used respectively to create and to store a :py:class:`~pyxel.detectors.Detector` to/from a file.

These models can be used when you want to store or to inject a :py:class:`~pyxel.detectors.Detector`
into the current :ref:`pipeline`.

.. _scene_generation_save_detector:

Save detector
-------------

This model saves the current :py:class:`~pyxel.detectors.Detector` into a file.
Accepted file formats are ``.h5``, ``.hdf5``, ``.hdf`` and ``.asdf``.

.. code-block:: yaml

    - name: save_detector
      func: pyxel.models.save_detector
      enabled: true
      arguments:
        filename: my_detector.h5

.. autofunction:: pyxel.models.save_detector
   :noindex:


.. _scene_generation_load_detector:

Load detector
-------------

This model loads a :py:class:`~pyxel.detectors.Detector` from a file and injects it in the current pipeline.
Accepted file formats are ``.h5``, ``.hdf5``, ``.hdf`` and ``.asdf``.

.. code-block:: yaml

    - name: load_detector
      func: pyxel.models.load_detector
      enabled: true
      arguments:
        filename: my_detector.h5

.. autofunction:: pyxel.models.load_detector
   :noindex:


.. _load_star_map:

Load star map
=============

:guilabel:`Scene` → :guilabel:`Scene`

Generate scene from `scopesim <https://scopesim.readthedocs.io/en/latest/>`_ Source object loading objects from the GAIA catalog for given coordinates and FOV.

Example of the configuration file:

.. code-block:: yaml

    - name: load_star_map
      func: pyxel.models.scene_generation.load_star_map
      enabled: true
      arguments:
        right_ascension: 56.75 # deg
        declination: 24.1167 # deg
        fov_radius: 0.5 # deg

.. autofunction:: load_star_map
