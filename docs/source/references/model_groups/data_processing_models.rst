.. _data_processing:

======================
Data Processing models
======================

.. currentmodule:: pyxel.models.data_processing

Data processing models are used to process data.
Result retrieved with run_mode() will show :py:class:`datatree.DataTree` structure containing two groups:

``Bucket`` group, containing the Scene, Photon, Charge, Pixel, Signal and Image, if initialized in the pipeline.

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

.. note::
    You can find examples of this model in these Jupyter Notebooks from `Pyxel Data <https://esa.gitlab.io/pyxel-data>`_:

    * :external+pyxel_data:doc:`examples/models/dark_current/dark_current_Si`
    * :external+pyxel_data:doc:`examples/models/data_processing/data_analysis/data_processing-obs`

.. autofunction:: statistics

.. _source_extractor:

Extract ROI
===========

Extracts the source data of the final pixel array and output in the form of an xarray dataset. The models makes use of
the `Photutils library <https://photutils.readthedocs.io/en/stable/>`_  and configured it into a library of
stand-alone functions and classes.

The `Photutils library <https://photutils.readthedocs.io/en/stable/>`_ is a useful post-processing tool capable of
calculating statistics of a given array.

.. code-block:: yaml

    data_processing:
      - name: source_extractor
        func: pyxel.models.data_processing.source_extractor
        arguments:
          thresh: 80
          minarea: 5
        enabled: true

.. note::
    You can find an example of this model used in this Jupyter Notebook
    :external+pyxel_data:doc:`examples/models/data_processing/source_extractor/SEP_exposure`
    from `Pyxel Data <https://esa.gitlab.io/pyxel-data>`_.

.. autofunction:: source_extractor

There is code within Pyxel capable of harnessing some data,
such as background subtraction and imaging a given 2D given numpy array.

.. autofunction:: plot_roi

.. _mean_variance:

Mean-variance
=============

Compute a **Mean-Variance** 1D array that represents the relationship between the mean signal of a detector and
its variance.

This is particularly useful for analyzing the statistical properties of image data,
such as determining the consistency of pixel values in a detector.

This model takes detector data (e.g., pixel, photon, image, or signal) and computes
the mean and variance of the specified data structure.
The results are stored within the detector's internal `.data` tree for further analysis or visualization.

**YAML configuration example:**

Below is an example of how to configure the **Mean-Variance** model in the Pyxel YAML configuration file:

.. code-block:: yaml

  data_processing:
    - name: mean_variance
      func: pyxel.models.data_processing.mean_variance
      enabled: true
      arguments:
        data_structure: image  # Options: 'pixel', 'photon', 'image', 'signal'

.. hint::

    .. code-block:: python

       >>> import pyxel
       >>> config = pyxel.load("configuration.yaml")

       >>> data_tree = pyxel.run_mode(
       ...     mode=config.running_mode,
       ...     detector=config.detector,
       ...     pipeline=config.pipeline,
       ... )

       >>> data_tree["/data/mean_variance/image/variance"]
       <xarray.DataTree 'image'>
       Group: /data/mean_variance/image
           Dimensions:      (pipeline_idx: 100)
           Coordinates:
             * pipeline_idx (pipeline_idx) int64 0 1 ... 98 99
           Data variables:
               mean         (pipeline_idx) float64 5.723e+03 1.144e+04 ... 5.238e+04 5.238e+04
               variance     (pipeline_idx) float64 3.238e+06 1.294e+07 2.91e+07 ... 4.03e+05 3.778e+05

       >>> (
       ...     data_tree["/data/mean_variance/image"]
       ...     .to_dataset()
       ...     .plot.scatter(x="mean", y="variance", xscale="log", yscale="log")
       ... )

   .. figure:: _static/mean_variance_plot.png
       :scale: 70%
       :alt: Mean-Variance plot
       :align: center

.. note::
    You can find an example of this model used in this Jupyter Notebook
    :external+pyxel_data:doc:`examples/models/data_processing/data_analysis/data_processing-obs`
    from `Pyxel Data <https://esa.gitlab.io/pyxel-data>`_.



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

.. note::
    You can find an example of this model used in this Jupyter Notebook
    :external+pyxel_data:doc:`examples/models/data_processing/data_analysis/data_processing-obs`
    from `Pyxel Data <https://esa.gitlab.io/pyxel-data>`_.

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

.. note::
    You can find an example of this model used in this Jupyter Notebook
    :external+pyxel_data:doc:`examples/models/data_processing/data_analysis/data_processing-obs`
    from `Pyxel Data <https://esa.gitlab.io/pyxel-data>`_.

.. autofunction:: signal_to_noise_ratio
