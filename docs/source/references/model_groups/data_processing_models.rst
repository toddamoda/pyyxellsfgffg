.. _data_processing:

======================
Data Processing models
======================

.. currentmodule:: pyxel.models.data_processing

Data processing models are used to process data.
Result retrieved with run_mode() will show :py:class:`datatree.DataTree` structure containing two groups:

``Bucket`` group, containing the Photon, Charge, Pixel, Signal and Image.

``Data`` group, containing processed data for each data processing model used in the YAML configuration file.

Processed data from models in the used in the YAML configuration file can be also accessed directly via ``detector.data``.

.. _data_processing_create_store_detector:

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

Extracts the source data of the final pixel array and output in the form of an xarray dataset. The models makes use of
the `SEP library <https://sep.readthedocs.io/en/v1.1.x/index.html>`_ which has taken the
`original source extractor <https://sep.readthedocs.io/en/v1.1.x/index.html>`_ package and configured it into a library of
stand-alone functions and classes.

The `SEP library <https://sep.readthedocs.io/en/v1.1.x/index.html>`_ is a useful post-processing tool capable of
calculating statistics of a given array.

.. code-block:: yaml

    data_processing:
      - name: extract_roi_to_xarray
        func: pyxel.models.data_processing.extract_roi_to_xarray
        arguments:
          thresh: 80
          minarea: 5
        enabled: true

.. autofunction:: extract_roi_to_xarray

There is code within Pyxel capable of harnessing some data,
such as background subtraction and imaging a given 2D given nupy array.

.. autofunction:: plot_roi

.. _mean_variance:

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

.. _linear_regression:

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

.. _remove_cosmic_rays:

Remove Cosmic Rays
==================

Removes cosmic rays from the pixel array using LACosmic package.

.. code-block:: yaml

  data_processing:
    - name: remove_cosmic_rays
      func: pyxel.models.data_processing.remove_cosmic_rays
      enabled: true
      arguments:
        contrast: 1.0
        cr_threshold: 50.0
        neighbor_threshold: 50.0
        effective_gain: 1.0
        readnoise: 0.0

.. autofunction:: remove_cosmic_rays

.. _snr:

Signal-to-noise ratio
=====================

The model :ref:`snr` can be used to get the signal-to-noise-ratio (SNR) along the time for of the data buckets
photon, pixel, signal and image of the detector. The ``data_structure`` "signal" is the one selected by default.

.. code-block:: yaml

    data_processing:
    - name: snr
      func: pyxel.models.data_processing.signal_to_noise_ratio
      enabled: true
      arguments:
        data_structure: "signal"

.. autofunction:: signal_to_noise_ratio
