.. _data_processing:

==========================
Data Processing models
==========================

.. currentmodule:: pyxel.models.data_processing

Data processing models are used to process data.
Result retrieved with run_mode() will show DataTree structure containing two groups:

``Bucket`` group, containing the Photon, Charge, Pixel, Signal and Image.

``Data`` group, containing processed data for each data processing model used in the YAML configuration file.

Processed data from models in the used in the YAML configuration file can be also accessed directly via ``detector.data``.


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

The model :ref:`statistics` can be used to do simple statistics computations,
giving the ``var``, ``mean``, ``min``, ``max`` and ``count`` of the data buckets
photon, pixel, signal and image of the detector.
The calculated statistics can then be accessed via ``detector.data.statistics``.


.. code-block:: yaml

    data_processing:
    - name: statistics
      func: pyxel.models.data_processing.statistics
      enabled: true


.. autofunction:: statistics

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

.. autofunction:: extract_roi_to_xarray


Mean-variance
=============

Compute a mean-variance 1D array that shows relationship between the mean signal of a detector and its variance.

.. code-block:: yaml

  data_processing:
    - name: mean_variance
      func: pyxel.models.data_processing.mean_variance
      enabled: true
      arguments:
        data_structure: image

.. autofunction:: mean_variance


Linear regression
=================

Compute a linear regression along readout time.

.. code-block:: yaml

  data_processing:
    - name: linear_regression
      func: pyxel.models.data_processing.linear_regression
      enabled: true
      arguments:
        data_structure: image

.. autofunction:: linear_regression
