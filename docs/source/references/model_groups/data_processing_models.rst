.. _data_processing:

==========================
Data Processing models
==========================

.. currentmodule:: pyxel.models.data_processing

Data processing models are used to process data.
TBW.


Create and Store a detector
===========================

The models :ref:`data_processing_save_detector` and :ref:`data_processing_load_detector`
can be used respectively to create and to store a :py:class:`~pyxel.detectors.Detector` to/from a file.

These models can be used when you want to store or to inject a :py:class:`~pyxel.detectors.Detector`
into the current :ref:`pipeline`.

.. _data_processing_save_detector:

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

.. _data_processing_load_detector:

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


.. _statistics:

Statistics
==========

The model :ref:`statistics` can be used to do simple statistics computations.
The calculated statistics can then be accessed via ``detector.processed_data.data``.


.. code-block:: yaml

    data_processing:
    - name: compute_statistics
      func: pyxel.models.data_processing.compute_statistics
      enabled: true


.. _extract_roi_to_xarray:

Extract ROI
===========

Extract the roi data converts it to xarray dataset and saves the information to the final result.

.. code-block:: yaml

    data_processing:
      - name: extract_roi_to_xarray
        func: pyxel.models.data_processing.extract_roi_to_xarray
        arguments:
          thresh: 80
          minarea: 5
        enabled: true
