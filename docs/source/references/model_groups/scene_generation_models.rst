.. _scene_generation:

========================
Scene Generation models
========================

.. currentmodule:: pyxel.models.scene_generation

Scene generation models are used to add a scene to :py:class:`~pyxel.data_structure.Scene` array
inside the :py:class:`~pyxel.detectors.Detector` object. At the beginning the :py:class:`~pyxel.data_structure.Scene`
array is an array of zeros. Multiple scene generation models can be linked together one after another.
The values in the :py:class:`~pyxel.data_structure.Scene` array represent photon flux,
so number of photons per pixel area per second. Time scale of the incoming flux can be changed in the model arguments.


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




.. _load_galaxy:

Load galaxy
==========

:guilabel:`Scene` → :guilabel:`Scene`


.. autofunction:: load_galaxy

