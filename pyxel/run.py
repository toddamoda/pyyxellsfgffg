#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""CLI to run Pyxel."""
import logging
import sys
import time
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

import click
import dask
import pandas as pd

from pyxel import Configuration
from pyxel import __version__ as version
from pyxel import load, outputs, save
from pyxel.detectors import APD, CCD, CMOS, MKID, Detector
from pyxel.exposure import Exposure
from pyxel.observation import Observation, ObservationResult
from pyxel.pipelines import DetectionPipeline, Processor
from pyxel.util import create_model, download_examples

if TYPE_CHECKING:
    import xarray as xr
    from datatree import DataTree

    from pyxel.calibration import Calibration
    from pyxel.outputs import CalibrationOutputs, ExposureOutputs, ObservationOutputs


# TODO: This function will be deprecated (see #563)
def exposure_mode(
    exposure: "Exposure",
    detector: Detector,
    pipeline: "DetectionPipeline",
) -> "xr.Dataset":
    """Run an 'exposure' pipeline.

    For more information, see :ref:`exposure_mode`.

    Parameters
    ----------
    exposure: Exposure
    detector: Detector
    pipeline: DetectionPipeline

    Returns
    -------
    Dataset
        An multi-dimensional array database from `xarray <https://xarray.pydata.org>`_.

    Examples
    --------
    Load a configuration file

    >>> import pyxel
    >>> config = pyxel.load("configuration.yaml")
    >>> config
    Configuration(...)

    Run an exposure pipeline

    >>> dataset = pyxel.exposure_mode(
    ...     exposure=config.exposure,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ... )
    >>> dataset
    <xarray.Dataset>
    Dimensions:       (readout_time: 1, y: 450, x: 450)
    Coordinates:
      * readout_time  (readout_time) int64 1
      * y             (y) int64 0 1 2 3 4 5 6 7 ... 442 443 444 445 446 447 448 449
      * x             (x) int64 0 1 2 3 4 5 6 7 ... 442 443 444 445 446 447 448 449
    Data variables:
        image         (readout_time, y, x) uint16 9475 9089 8912 ... 9226 9584 10079
        signal        (readout_time, y, x) float64 3.159 3.03 2.971 ... 3.195 3.36
        pixel         (readout_time, y, x) float64 1.053e+03 1.01e+03 ... 1.12e+03
    """

    logging.info("Mode: Exposure")

    exposure_outputs: ExposureOutputs = exposure.outputs

    processor = Processor(detector=detector, pipeline=pipeline)

    result: xr.Dataset = exposure.run_exposure(processor=processor)

    if exposure_outputs.save_exposure_data:
        exposure_outputs.save_exposure_outputs(dataset=result)

    return result


def _run_exposure_mode(
    exposure: "Exposure",
    detector: Detector,
    pipeline: "DetectionPipeline",
    with_intermediate_steps: bool,
) -> "DataTree":
    """Run an 'exposure' pipeline.

    For more information, see :ref:`exposure_mode`.

    Parameters
    ----------
    exposure : Exposure
    detector : Detector
    pipeline : DetectionPipeline
    with_intermediate_steps : bool

    Returns
    -------
    DataTree
        An multi-dimensional tree of arrays.

    Examples
    --------
    Load a configuration file

    >>> import pyxel
    >>> config = pyxel.load("configuration.yaml")
    >>> config
    Configuration(...)

    Run an exposure pipeline

    >>> data_tree = pyxel._run_exposure_mode(
    ...     exposure=config.exposure,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ... )
    >>> data_tree
    DataTree('None', parent=None)
    │   Dimensions:  (time: 54, y: 100, x: 100)
    │   Coordinates:
    │     * time     (time) float64 0.02 0.06 0.12 0.2 0.3 ... 113.0 117.8 122.7 127.7
    │     * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
    │     * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
    │   Data variables:
    │       photon   (time, y, x) float64 102.0 108.0 79.0 ... 2.513e+04 2.523e+04
    │       charge   (time, y, x) float64 201.0 193.0 173.0 ... 2.523e+04 2.532e+04
    │       pixel    (time, y, x) float64 94.68 98.18 71.82 ... 2.388e+04 2.418e+04
    │       signal   (time, y, x) float64 0.001176 0.00129 0.0007866 ... 0.2946 0.2982
    │       image    (time, y, x) float64 20.0 22.0 13.0 ... 4.826e+03 4.887e+03
    │   Attributes:
    │       pyxel version:  1.9.1+104.g9da11bb2.dirty
    │       running mode:   Exposure
    └── DataTree('data')
        └── DataTree('mean_variance')
            └── DataTree('image')
                    Dimensions:   (mean: 54)
                    Coordinates:
                      * mean      (mean) float64 19.58 38.7 57.83 ... 4.586e+03 4.681e+03 4.776e+03
                    Data variables:
                        variance  (mean) float64 5.958 10.28 14.82 ... 1.25e+04 1.3e+04 1.348e+04
    """

    logging.info("Mode: Exposure")

    exposure_outputs: ExposureOutputs = exposure.outputs

    processor = Processor(detector=detector, pipeline=pipeline)

    result: DataTree = exposure.run_exposure_new(
        processor=processor,
        with_intermediate_steps=with_intermediate_steps,
    )

    if exposure_outputs.save_exposure_data:
        exposure_outputs.save_exposure_outputs(dataset=result)

    return result


# TODO: This function will be deprecated (see #563)
def observation_mode(
    observation: "Observation",
    detector: Detector,
    pipeline: "DetectionPipeline",
) -> "ObservationResult":
    """Run an 'observation' pipeline.

    For more information, see :ref:`observation_mode`.

    Parameters
    ----------
    observation: Observation
    detector: Detector
    pipeline: DetectionPipeline

    Returns
    -------
    ObservationResult
        Result.

    Examples
    --------
    Load a configuration file

    >>> import pyxel
    >>> config = pyxel.load("configuration.yaml")
    >>> config
    Configuration(...)

    Run an observation pipeline

    >>> result = pyxel.observation_mode(
    ...     exposure=config.exposure,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ... )
    >>> result
    ObservationResult(...)
    """
    logging.info("Mode: Observation")

    observation_outputs: ObservationOutputs = observation.outputs

    # TODO: This should be done during initializing of object `Configuration`
    # parametric_outputs.params_func(parametric)

    processor = Processor(detector=detector, pipeline=pipeline)

    result: ObservationResult = observation.run_observation(processor=processor)

    if observation_outputs.save_observation_data:
        observation_outputs.save_observation_datasets(
            result=result, mode=observation.parameter_mode
        )

    return result


# TODO: This function will be deprecated (see #563)
def calibration_mode(
    calibration: "Calibration",
    detector: Detector,
    pipeline: "DetectionPipeline",
    compute_and_save: bool = True,
) -> tuple["xr.Dataset", pd.DataFrame, pd.DataFrame, Sequence]:
    """Run a 'calibration' pipeline.

    For more information, see :ref:`calibration_mode`.

    Parameters
    ----------
    calibration: Calibration
    detector: Detector
    pipeline: DetectionPipeline
    compute_and_save: bool

    Returns
    -------
    tuple of Dataset, DataFrame, DataFrame, Sequence

    Examples
    --------
    Load a configuration file

    >>> import pyxel
    >>> config = pyxel.load("configuration.yaml")
    >>> config
    Configuration(...)

    Run a calibration pipeline

    >>> ds, processors, logs, filenames = pyxel.calibration_mode(
    ...     exposure=config.exposure,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ... )

    >>> ds
    <xarray.Dataset>
    Dimensions:              (island: 2, evolution: 2, param_id: 4, id_processor: 1, readout_time: 1, y: 100, x: 100)
    Coordinates:
      * island               (island) int64 1 2
      * evolution            (evolution) int64 1 2
      * id_processor         (id_processor) int64 0
      * readout_time         (readout_time) int64 1
      * y                    (y) int64 0 1 2 3 4 5 6 7 8 ... 92 93 94 95 96 97 98 99
      * x                    (x) int64 0 1 2 3 4 5 6 7 8 ... 92 93 94 95 96 97 98 99
      * param_id             (param_id) int64 0 1 2 3
    Data variables:
        champion_fitness     (island, evolution) float64 4.759e+06 ... 4.533e+06
        champion_decision    (island, evolution, param_id) float64 0.08016 ... 7....
        champion_parameters  (island, evolution, param_id) float64 0.08016 ... 7....
        simulated_image      (island, id_processor, readout_time, y, x) uint16 48...
        simulated_signal     (island, id_processor, readout_time, y, x) float64 4...
        simulated_pixel      (island, id_processor, readout_time, y, x) float64 6...
        target               (id_processor, y, x) >f8 4.834e+03 ... 4.865e+03
    Attributes:
        num_islands:      2
        population_size:  20
        num_evolutions:   2
        generations:      5
        topology:         unconnected
        result_type:      image

    >>> processors
           island  id_processor                                          processor
    0       0             0  Delayed('apply_parameters-c5da1649-766f-4ecb-a...
    1       1             0  Delayed('apply_parameters-c16f998f-f52f-4beb-b...

    >>> logs
        num_generations  ...  global_num_generations
    0                 1  ...                       1
    1                 2  ...                       2
    2                 3  ...                       3
    3                 4  ...                       4
    4                 5  ...                       5
    ..              ...  ...                     ...
    15                1  ...                       6
    16                2  ...                       7
    17                3  ...                       8
    18                4  ...                       9
    19                5  ...                      10

    >>> filenames
    []
    """
    # Late import to speedup start-up time
    from pyxel.calibration import CalibrationResult

    logging.info("Mode: Calibration")

    calibration_outputs: CalibrationOutputs = calibration.outputs

    processor = Processor(detector=detector, pipeline=pipeline)

    ds_results, df_processors, df_all_logs = calibration.run_calibration(
        processor=processor, output_dir=calibration_outputs.output_dir
    )

    # TODO: Save the processors from 'df_processors'
    # TODO: Generate plots from 'ds_results'

    # TODO: Do something with 'df_all_logs' ?

    # TODO: create 'output' object with .calibration_outputs
    # TODO: use 'fitting.get_simulated_data' ==> np.ndarray

    # geometry = processor.detector.geometry
    # calibration.post_processing(
    #     champions=champions,
    #     output=calibration_outputs,
    #     row=geometry.row,
    #     col=geometry.col,
    # )
    filenames = calibration._post_processing(
        ds=ds_results, df_processors=df_processors, output=calibration_outputs
    )

    if compute_and_save:
        computed_ds, df_processors, df_logs, filenames = dask.compute(
            ds_results, df_processors, df_all_logs, filenames
        )

        if calibration_outputs.save_calibration_data:
            calibration_outputs.save_calibration_outputs(
                dataset=computed_ds, logs=df_logs
            )
            print(f"Saved calibration outputs to {calibration_outputs.output_dir}")

        result = CalibrationResult(
            dataset=computed_ds,
            processors=df_processors,
            logs=df_logs,
            filenames=filenames,
        )

    else:
        result = CalibrationResult(
            dataset=ds_results,
            processors=df_processors,
            logs=df_all_logs,
            filenames=filenames,
        )

    return result


def _run_calibration_mode(
    calibration: "Calibration",
    detector: Detector,
    pipeline: "DetectionPipeline",
) -> "DataTree":
    """Run a 'Calibration' pipeline.

    Parameters
    ----------
    calibration : Calibration
    detector : Detector
    pipeline : DetectionPipeline

    Notes
    -----
    This is a 'private' function called by 'run_mode'.

    Returns
    -------
    DataTree

    Examples
    --------
    >>> data_tree = _run_calibration_mode(calibration=..., detector=..., pipeline=...)
    >>> data_tree
    DataTree('None', parent=None)
    │   Dimensions:              (evolution: 5, island: 1, param_id: 4, individual: 10,
    │                             processor: 10, readout_time: 1, y: 235, x: 1)
    │   Coordinates:
    │     * evolution            (evolution) int64 0 1 2 3 4
    │     * island               (island) int64 0
    │     * param_id             (param_id) int64 0 1 2 3
    │     * individual           (individual) int64 0 1 2 3 4 5 6 7 8 9
    │     * processor            (processor) int64 0 1 2 3 4 5 6 7 8 9
    │     * readout_time         (readout_time) int64 1
    │     * y                    (y) int64 2065 2066 2067 2068 ... 2296 2297 2298 2299
    │     * x                    (x) int64 0
    │   Data variables:
    │       champion_fitness     (island, evolution) float64 3.271e+06 ... 4.641e+05
    │       champion_decision    (island, evolution, param_id) float64 -2.224 ... 3.662
    │       champion_parameters  (island, evolution, param_id) float64 0.00597 ... 4....
    │       best_fitness         (island, evolution, individual) float64 3.271e+06 .....
    │       best_decision        (island, evolution, individual, param_id) float64 -2...
    │       best_parameters      (island, evolution, individual, param_id) float64 0....
    │       simulated_photon     (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       simulated_charge     (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       simulated_pixel      (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       simulated_signal     (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       simulated_image      (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       target               (processor, y, x) float64 13.75 0.4567 ... 0.2293 0.375
    │   Attributes:
    │       num_islands:      1
    │       population_size:  10
    │       num_evolutions:   5
    │       generations:      1
    │       topology:         fully_connected
    │       result_type:      pixel
    └── DataTree('full_size')
            Dimensions:           (island: 1, processor: 10, readout_time: 1, y: 2300, x: 1)
            Coordinates:
              * island            (island) int64 0
              * processor         (processor) int64 0 1 2 3 4 5 6 7 8 9
              * readout_time      (readout_time) int64 1
              * y                 (y) int64 0 1 2 3 4 5 6 ... 2294 2295 2296 2297 2298 2299
              * x                 (x) int64 0
            Data variables:
                simulated_photon  (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                simulated_charge  (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                simulated_pixel   (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                simulated_signal  (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                simulated_image   (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                target            (processor, y, x) float64 0.0 0.4285 ... 0.2293 0.375
    """
    logging.info("Mode: Calibration")

    calibration_outputs: CalibrationOutputs = calibration.outputs

    processor = Processor(detector=detector, pipeline=pipeline)

    data_tree = calibration.run_calibration_new(
        processor=processor,
        output_dir=calibration_outputs.output_dir,
    )

    return data_tree


def _run_observation_mode(
    observation: Observation,
    detector: Detector,
    pipeline: DetectionPipeline,
) -> "DataTree":
    logging.info("Mode: Observation")

    observation_outputs: ObservationOutputs = observation.outputs

    processor = Processor(detector=detector, pipeline=pipeline)

    result = observation.run_observation_datatree(processor=processor)

    if observation_outputs.save_observation_data:
        raise NotImplementedError
    #     observation_outputs.save_observation_datasets(
    #         result=result, mode=observation.parameter_mode
    #     )

    return result


def run_mode(
    mode: Union[Exposure, Observation, "Calibration"],
    detector: Detector,
    pipeline: DetectionPipeline,
    with_intermediate_steps: bool = False,
) -> "DataTree":
    """Run a pipeline.

    Parameters
    ----------
    mode : Exposure, Observation or Calibration
        Mode to execute.
    detector : Detector
        This object is the container for all the data used for the models.
    pipeline : DetectionPipeline
        This is the core algorithm of Pyxel. This pipeline contains all the models to run.
    with_intermediate_steps : bool, default: False
        Add all intermediate steps into the results as a ``DataTree``. This mode is used for debugging.


    Notes
    -----
    Parameter ``with_intermediate_steps`` is not (yet) stable and may change in the future.

    Returns
    -------
    DataTree

    Raises
    ------
    TypeError
        Raised if the ``mode`` is not valid.

    NotImplementedError
        Raised if parameter ``with_intermediate_steps`` is activated and `mode` is not an ``Exposure`` object.

    Examples
    --------
    Load a configuration file

    >>> import pyxel
    >>> config = pyxel.load("exposure_configuration.yaml")
    >>> config

     Run a 'Exposure' pipeline

    >>> data = pyxel.run_mode(
    ...     mode=config.exposure,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ... )
    >>> data
    DataTree('None', parent=None)
    │   Dimensions:  (time: 54, y: 100, x: 100)
    │   Coordinates:
    │     * time     (time) float64 0.02 0.06 0.12 0.2 0.3 ... 113.0 117.8 122.7 127.7
    │     * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
    │     * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
    │   Data variables:
    │       photon   (time, y, x) float64 85.0 120.0 109.0 ... 2.533e+04 2.51e+04
    │       charge   (time, y, x) float64 201.0 196.0 202.0 ... 2.543e+04 2.52e+04
    │       pixel    (time, y, x) float64 77.38 110.0 99.09 ... 2.406e+04 2.406e+04
    │       signal   (time, y, x) float64 0.0009377 0.001322 0.00133 ... 0.2968 0.2968
    │       image    (time, y, x) float64 16.0 22.0 22.0 ... 4.863e+03 4.863e+03
    │   Attributes:
    │       pyxel version:  1.9.1+104.g9da11bb2
    │       running mode:   Exposure
    ├── DataTree('scene')
    │   └── DataTree('list')
    │       └── DataTree('0')
    │               Dimensions:     (ref: 345, wavelength: 343)
    │               Coordinates:
    │                 * ref         (ref) int64 0 1 2 3 4 5 6 7 ... 337 338 339 340 341 342 343 344
    │                 * wavelength  (wavelength) float64 336.0 338.0 340.0 ... 1.018e+03 1.02e+03
    │               Data variables:
    │                   x           (ref) float64 2.057e+05 2.058e+05 ... 2.031e+05 2.03e+05
    │                   y           (ref) float64 8.575e+04 8.58e+04 ... 8.795e+04 8.807e+04
    │                   weight      (ref) float64 11.49 14.13 15.22 14.56 ... 15.21 11.51 8.727
    │                   flux        (ref, wavelength) float64 0.03769 0.04137 ... 1.813 1.896
    └── DataTree('data')
        ├── DataTree('mean_variance')
        │   └── DataTree('image')
        │           Dimensions:   (mean: 54)
        │           Coordinates:
        │             * mean      (mean) float64 19.64 38.7 57.77 ... 4.586e+03 4.682e+03 4.777e+03
        │           Data variables:
        │               variance  (mean) float64 5.893 10.36 15.13 ... 1.235e+04 1.297e+04 1.342e+04
        └── DataTree('statistics')
            └── DataTree('pixel')
                    Dimensions:  (time: 54)
                    Coordinates:
                      * time     (time) float64 0.02 0.06 0.12 0.2 0.3 ... 113.0 117.8 122.7 127.7
                    Data variables:
                        var      (time) float64 92.4 197.8 317.2 ... 3.027e+05 3.175e+05 3.286e+05
                        mean     (time) float64 94.64 189.1 283.5 ... 2.269e+04 2.316e+04 2.363e+04
                        min      (time) float64 63.39 134.9 220.3 ... 2.135e+04 2.193e+04 2.24e+04
                        max      (time) float64 134.8 248.1 359.7 ... 2.522e+04 2.569e+04 2.64e+04
                        count    (time) float64 1e+04 1e+04 1e+04 1e+04 ... 1e+04 1e+04 1e+04 1e+04

    Run a 'Calibration' pipeline

    >>> config = pyxel.load("calibration_configuration.yaml")
    >>> data = pyxel.run_mode(
    ...     mode=config.exposure,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ... )
    >>> data
    DataTree('None', parent=None)
    │   Dimensions:              (evolution: 5, island: 1, param_id: 4, individual: 10,
    │                             processor: 10, readout_time: 1, y: 235, x: 1)
    │   Coordinates:
    │     * evolution            (evolution) int64 0 1 2 3 4
    │     * island               (island) int64 0
    │     * param_id             (param_id) int64 0 1 2 3
    │     * individual           (individual) int64 0 1 2 3 4 5 6 7 8 9
    │     * processor            (processor) int64 0 1 2 3 4 5 6 7 8 9
    │     * readout_time         (readout_time) int64 1
    │     * y                    (y) int64 2065 2066 2067 2068 ... 2296 2297 2298 2299
    │     * x                    (x) int64 0
    │   Data variables:
    │       champion_fitness     (island, evolution) float64 3.271e+06 ... 4.641e+05
    │       champion_decision    (island, evolution, param_id) float64 -2.224 ... 3.662
    │       champion_parameters  (island, evolution, param_id) float64 0.00597 ... 4....
    │       best_fitness         (island, evolution, individual) float64 3.271e+06 .....
    │       best_decision        (island, evolution, individual, param_id) float64 -2...
    │       best_parameters      (island, evolution, individual, param_id) float64 0....
    │       simulated_photon     (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       simulated_charge     (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       simulated_pixel      (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       simulated_signal     (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       simulated_image      (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 235, 1), meta=np.ndarray>
    │       target               (processor, y, x) float64 13.75 0.4567 ... 0.2293 0.375
    │   Attributes:
    │       num_islands:      1
    │       population_size:  10
    │       num_evolutions:   5
    │       generations:      1
    │       topology:         fully_connected
    │       result_type:      pixel
    └── DataTree('full_size')
            Dimensions:           (island: 1, processor: 10, readout_time: 1, y: 2300, x: 1)
            Coordinates:
              * island            (island) int64 0
              * processor         (processor) int64 0 1 2 3 4 5 6 7 8 9
              * readout_time      (readout_time) int64 1
              * y                 (y) int64 0 1 2 3 4 5 6 ... 2294 2295 2296 2297 2298 2299
              * x                 (x) int64 0
            Data variables:
                simulated_photon  (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                simulated_charge  (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                simulated_pixel   (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                simulated_signal  (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                simulated_image   (island, processor, readout_time, y, x) float64 dask.array<chunksize=(1, 1, 1, 2300, 1), meta=np.ndarray>
                target            (processor, y, x) float64 0.0 0.4285 ... 0.2293 0.375

    Run a pipeline with all intermediate steps

    >>> results = pyxel.run_mode(
    ...     mode=config.exposure,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ...     with_intermediate_steps=True,
    ... )
    >>> results["/data/intermediate"]
    DataTree('intermediate', parent="data")
    │   Dimensions:  ()
    │   Data variables:
    │       *empty*
    │   Attributes:
    │       long_name:  Store all intermediate results modified along a pipeline
    └── DataTree('idx_0')
        │   Dimensions:  ()
        │   Data variables:
        │       *empty*
        │   Attributes:
        │       long_name:       Pipeline for one unique time
        │       pipeline_count:  0
        │       time:            1.0 s
        ├── DataTree('photon_collection')
        │   │   Dimensions:  ()
        │   │   Data variables:
        │   │       *empty*
        │   │   Attributes:
        │   │       long_name:  Model group: 'photon_collection'
        │   └── DataTree('load_image')
        │           Dimensions:  (y: 100, x: 100)
        │           Coordinates:
        │             * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        │             * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        │           Data variables:
        │               photon   (y, x) float64 1.515e+04 1.592e+04 ... 1.621e+04 1.621e+04
        │           Attributes:
        │               long_name:  Group: 'load_image'
        ├── DataTree('charge_generation')
        │   │   Dimensions:  ()
        │   │   Data variables:
        │   │       *empty*
        │   │   Attributes:
        │   │       long_name:  Model group: 'charge_generation'
        │   └── DataTree('photoelectrons')
        │           Dimensions:  (y: 100, x: 100)
        │           Coordinates:
        │             * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        │             * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        │           Data variables:
        │               charge   (y, x) float64 1.515e+04 1.592e+04 ... 1.621e+04 1.621e+04
        │           Attributes:
        │               long_name:  Group: 'photoelectrons'
        ├── DataTree('charge_collection')
        │   │   Dimensions:  ()
        │   │   Data variables:
        │   │       *empty*
        │   │   Attributes:
        │   │       long_name:  Model group: 'charge_collection'
        │   └── DataTree('simple_collection')
        │           Dimensions:  (y: 100, x: 100)
        │           Coordinates:
        │             * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        │             * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        │           Data variables:
        │               pixel    (y, x) float64 1.515e+04 1.592e+04 ... 1.621e+04 1.621e+04
        │           Attributes:
        │               long_name:  Group: 'simple_collection'
        ├── DataTree('charge_measurement')
        │   │   Dimensions:  ()
        │   │   Data variables:
        │   │       *empty*
        │   │   Attributes:
        │   │       long_name:  Model group: 'charge_measurement'
        │   └── DataTree('simple_measurement')
        │           Dimensions:  (y: 100, x: 100)
        │           Coordinates:
        │             * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        │             * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        │           Data variables:
        │               signal   (y, x) float64 0.04545 0.04776 0.04634 ... 0.05004 0.04862 0.04862
        │           Attributes:
        │               long_name:  Group: 'simple_measurement'
        └── DataTree('readout_electronics')
            │   Dimensions:  ()
            │   Data variables:
            │       *empty*
            │   Attributes:
            │       long_name:  Model group: 'readout_electronics'
            └── DataTree('simple_adc')
                    Dimensions:  (y: 100, x: 100)
                    Coordinates:
                      * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
                      * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
                    Data variables:
                        image    (y, x) uint32 298 314 304 304 304 314 ... 325 339 339 328 319 319
                    Attributes:
                        long_name:  Group: 'simple_adc'
    """
    from pyxel.calibration import Calibration

    if with_intermediate_steps and isinstance(mode, (Observation, Calibration)):
        raise NotImplementedError(
            "Parameter 'with_intermediate_steps' is not implemented for 'Observation'"
            " and 'Calibration' modes."
        )

    if isinstance(mode, Exposure):
        data_tree = _run_exposure_mode(
            exposure=mode,
            detector=detector,
            pipeline=pipeline,
            with_intermediate_steps=with_intermediate_steps,
        )

    elif isinstance(mode, Observation):
        data_tree = _run_observation_mode(
            observation=mode,
            detector=detector,
            pipeline=pipeline,
        )

    elif isinstance(mode, Calibration):
        data_tree = _run_calibration_mode(
            calibration=mode,
            detector=detector,
            pipeline=pipeline,
        )

    else:
        raise TypeError("Please provide a valid simulation mode !")

    return data_tree


def output_directory(configuration: Configuration) -> Path:
    """Return the output directory from the configuration.

    Parameters
    ----------
    configuration

    Returns
    -------
    output_dir
    """
    # Late import to speedup start-up time
    from pyxel.calibration import Calibration

    if isinstance(configuration.exposure, Exposure):
        output_dir = configuration.exposure.outputs.output_dir
    elif isinstance(configuration.calibration, Calibration):
        output_dir = configuration.calibration.outputs.output_dir
    elif isinstance(configuration.observation, Observation):
        output_dir = configuration.observation.outputs.output_dir
    else:
        raise (TypeError("Outputs not initialized."))
    return output_dir


def run(input_filename: Union[str, Path], random_seed: Optional[int] = None) -> None:
    """Run a YAML configuration file.

    For more information, see :ref:`running_modes`.

    Parameters
    ----------
    input_filename : str or Path
    random_seed : int, optional

    Examples
    --------
    >>> import pyxel
    >>> pyxel.run("configuration.yaml")
    """
    # Late import to speedup start-up time

    logging.info("Pyxel version %s", version)
    logging.info("Pipeline started.")

    start_time = time.time()

    configuration: Configuration = load(Path(input_filename).expanduser().resolve())

    output_dir = output_directory(configuration)

    save(input_filename=input_filename, output_dir=output_dir)

    pipeline: DetectionPipeline = configuration.pipeline
    detector: Union[CCD, CMOS, MKID, APD] = configuration.detector
    running_mode: Union[Exposure, Observation, Calibration] = configuration.running_mode

    _ = run_mode(mode=running_mode, detector=detector, pipeline=pipeline)

    logging.info("Pipeline completed.")
    logging.info("Running time: %.3f seconds", (time.time() - start_time))
    # Closing the logger in order to be able to move the file in the output dir
    logging.shutdown()
    outputs.save_log_file(output_dir)

    # Late import to speedup start-up time
    from matplotlib import pyplot as plt

    plt.close()


# TODO: Add an option to display colors ?
@click.group()
@click.version_option(version=version)
def main():
    """Pyxel detector simulation framework.

    Pyxel is a detector simulation framework, that can simulate a variety of
    detector effects (e.g., cosmic rays, radiation-induced :term:`CTI` in :term:`CCDs<CCD>`, persistence
    in :term:`MCT`, charge diffusion, crosshatches, noises, crosstalk etc.) on a given image.
    """


@main.command(name="download-examples")
@click.argument("folder", type=click.Path(), default="pyxel-examples", required=False)
@click.option("-f", "--force", is_flag=True, help="Force flag for saving the examples.")
def download_pyxel_examples(folder, force: bool):
    """Install examples to a specified directory.

    Default folder is './pyxel-examples'.
    """
    download_examples(foldername=folder, force=force)


@main.command(name="create-model")
@click.argument("model_name", type=str)
def create_new_model(model_name: str):
    """Create a new model.

    Use: arg1/arg2. Create a new module in ``pyxel/models/arg1/arg2`` using a template
    (``pyxel/templates/MODELTEMPLATE.py``)
    """
    create_model(newmodel=model_name)


@main.command(name="run")
@click.argument("config", type=click.Path(exists=True))
@click.option(
    "-v",
    "--verbosity",
    count=True,
    show_default=True,
    help="Increase output verbosity (-v/-vv/-vvv)",
)
def run_config(config: str, verbosity: int):
    """Run Pyxel with a ``YAML`` configuration file."""
    logging_level = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG][
        min(verbosity, 3)
    ]
    log_format = (
        "%(asctime)s - %(name)s - %(threadName)30s - %(funcName)30s \t %(message)s"
    )
    logging.basicConfig(
        filename="pyxel.log",
        level=logging_level,
        format=log_format,
        datefmt="%d-%m-%Y %H:%M:%S",
    )

    # If user wants the log in stdout AND in file, use the three lines below
    stream_stdout = logging.StreamHandler(sys.stdout)
    stream_stdout.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(stream_stdout)

    run(input_filename=config)


if __name__ == "__main__":
    main()
