.. _apireference:

=============
API reference
=============

This page provides an auto-generated summary of Pyxel's API.

Top-level functions
===================

.. currentmodule:: pyxel

.. autosummary::

    load
    run_mode
    run
    show_versions

Configuration
=============

.. autosummary::

    Configuration
    copy_config_file

Data structures
===============

.. currentmodule:: pyxel.data_structure

.. autosummary::

    Photon
    Pixel
    Phase
    Signal
    Image
    Charge
    Array

Detectors
=========

.. currentmodule:: pyxel.detectors

.. autosummary::

    CCD
    CMOS
    MKID
    APD
    Detector

Attributes
----------

.. autosummary::

    Detector.geometry
    Detector.characteristics
    Detector.scene
    Detector.photon
    Detector.charge
    Detector.pixel
    Detector.signal
    Detector.image
    Detector.data
    Detector.intermediate

Properties
----------

.. currentmodule:: pyxel.detectors

.. autosummary::

    Environment
    Characteristics
    Geometry
    ReadoutProperties
    CCDGeometry
    CMOSGeometry
    MKIDGeometry
    APDCharacteristics
    APDGeometry

Readout time
------------

.. autosummary::

    Detector.set_readout
    Detector.readout_properties
    Detector.time
    Detector.start_time
    Detector.absolute_time
    Detector.time_step
    Detector.times_linear
    Detector.num_steps
    Detector.pipeline_count
    Detector.is_first_readout
    Detector.is_last_readout
    Detector.read_out
    Detector.is_dynamic
    Detector.non_destructive_readout
    Detector.has_persistence
    Detector.persistence
    Detector.numbytes
    Detector.memory_usage

Input / Output
--------------

.. autosummary::

    Detector.load
    Detector.save
    Detector.from_hdf5
    Detector.to_hdf5
    Detector.from_asdf
    Detector.to_asdf
    Detector.to_xarray
    Detector.to_dict
    Detector.from_dict


Deprecated / Pending deprecation
================================

.. currentmodule:: pyxel

.. autosummary::

    exposure_mode
    observation_mode
    calibration_mode



* :ref:`pipelines_api`
* :ref:`exposure_api`
* :ref:`observation_api`
* :ref:`calibration_api`
* :ref:`inputs_api`
* :ref:`outputs_api`
* :ref:`notebook_api`
* :ref:`util_api`

.. toctree::
   :caption: api reference
   :maxdepth: 1
   :hidden:

   api/run.rst
   api/configuration.rst
   api/datastructures.rst
   api/detectors.rst
   api/detectorproperties.rst
   api/pipelines.rst
   api/exposure.rst
   api/observation.rst
   api/calibration.rst
   api/inputs.rst
   api/outputs.rst
   api/notebook.rst
   api/util.rst
