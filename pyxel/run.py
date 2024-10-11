#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""CLI to run Pyxel."""

import logging
import platform
import sys
import time
import warnings
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

import click

from pyxel import Configuration
from pyxel import __version__ as version
from pyxel import copy_config_file, load, outputs
from pyxel.detectors import APD, CCD, CMOS, MKID, Detector
from pyxel.exposure import Exposure
from pyxel.observation import Observation
from pyxel.observation.deprecated import _run_observation_deprecated
from pyxel.pipelines import DetectionPipeline, Processor
from pyxel.pipelines.processor import _get_obj_att
from pyxel.util import create_model, create_model_to_console, download_examples

if TYPE_CHECKING:
    import pandas as pd
    import xarray as xr

    # Import 'DataTree'
    try:
        from xarray.core.datatree import DataTree
    except ImportError:
        from datatree import DataTree  # type: ignore[assignment]

    from pyxel.calibration import Calibration
    from pyxel.observation.deprecated import ObservationResult
    from pyxel.outputs import CalibrationOutputs, ExposureOutputs, ObservationOutputs


def exposure_mode(
    exposure: "Exposure",
    detector: Detector,
    pipeline: "DetectionPipeline",
) -> "xr.Dataset":  # pragma: no cover
    """Run an 'exposure' pipeline.

    .. deprecated:: 1.14
        `exposure_mode` will be removed in pyxel 2.0.0, it is replaced by `pyxel.run_mode`.

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
    warnings.warn("Use function 'pyxel.run_mode'", FutureWarning, stacklevel=1)

    logging.info("Mode: Exposure")

    # Create an output folder
    outputs: Optional[ExposureOutputs] = exposure.outputs
    if outputs:
        outputs.create_output_folder()

    processor = Processor(detector=detector, pipeline=pipeline)

    result: xr.Dataset = exposure._run_exposure_deprecated(processor=processor)

    if outputs and outputs.save_exposure_data:
        outputs.save_exposure_outputs(dataset=result)

    return result


def _run_exposure_mode_without_datatree(
    exposure: "Exposure",
    processor: Processor,
) -> None:
    """Run an 'exposure' pipeline.

    For more information, see :ref:`exposure_mode`.

    Parameters
    ----------
    exposure : Exposure
    processor : Detector

    Returns
    -------
    None
    """

    logging.info("Mode: Exposure")

    # Create an output folder
    outputs: Optional[ExposureOutputs] = exposure.outputs
    if outputs:
        outputs.create_output_folder()

    _ = exposure.run_exposure(
        processor=processor,
        debug=False,
        with_inherited_coords=False,
    )


def _run_exposure_mode(
    exposure: "Exposure",
    processor: Processor,
    debug: bool,
    with_inherited_coords: bool,
) -> "DataTree":
    """Run an 'exposure' pipeline.

    For more information, see :ref:`exposure_mode`.

    Parameters
    ----------
    exposure : Exposure
    processor : Detector
    debug : bool

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

    # Create an output folder
    outputs: Optional[ExposureOutputs] = exposure.outputs
    if outputs:
        outputs.create_output_folder()

    result: DataTree = exposure.run_exposure(
        processor=processor,
        debug=debug,
        with_inherited_coords=with_inherited_coords,
    )

    if outputs and outputs.save_exposure_data:
        outputs.save_exposure_outputs(dataset=result)

    return result


def observation_mode(
    observation: "Observation",
    detector: Detector,
    pipeline: "DetectionPipeline",
) -> "ObservationResult":  # pragma: no cover
    """Run an 'observation' pipeline.

    .. deprecated:: 1.14
        `observation_mode` will be removed in pyxel 2.0.0, it is replaced by `pyxel.run_mode`.

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
    warnings.warn("Use function 'pyxel.run_mode'", FutureWarning, stacklevel=1)

    logging.info("Mode: Observation")

    # Create an output folder
    outputs: Optional[ObservationOutputs] = observation.outputs
    if outputs:
        outputs.create_output_folder()

    # TODO: This should be done during initializing of object `Configuration`
    # parametric_outputs.params_func(parametric)

    processor = Processor(detector=detector, pipeline=pipeline)

    result: "ObservationResult" = _run_observation_deprecated(
        observation, processor=processor
    )

    if outputs and outputs.save_observation_data:
        outputs._save_observation_datasets_deprecated(
            result=result, mode=observation.parameter_mode
        )

    return result


def calibration_mode(
    calibration: "Calibration",
    detector: Detector,
    pipeline: "DetectionPipeline",
    compute_and_save: bool = True,
) -> tuple["xr.Dataset", "pd.DataFrame", "pd.DataFrame", Sequence]:  # pragma: no cover
    """Run a 'calibration' pipeline.

    .. deprecated:: 1.14
        `calibration_mode` will be removed in pyxel 2.0.0, it is replaced by `pyxel.run_mode`.

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
    import dask

    warnings.warn("Use function 'pyxel.run_mode'", FutureWarning, stacklevel=1)

    from pyxel.calibration import CalibrationResult

    logging.info("Mode: Calibration")

    # Create an output folder
    outputs: Optional[CalibrationOutputs] = calibration.outputs
    if outputs:
        outputs.create_output_folder()

    processor = Processor(detector=detector, pipeline=pipeline)

    ds_results, df_processors, df_all_logs = calibration._run_calibration_deprecated(
        processor=processor,
        output_dir=outputs.current_output_folder if outputs else None,
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
        ds=ds_results,
        df_processors=df_processors,
        output=outputs,
    )

    if compute_and_save:
        computed_ds, df_processors, df_logs, filenames = dask.compute(
            ds_results, df_processors, df_all_logs, filenames
        )

        if outputs and outputs._save_calibration_data_deprecated:
            outputs._save_calibration_outputs_deprecated(
                dataset=computed_ds, logs=df_logs
            )
            print(f"Saved calibration outputs to {outputs.current_output_folder}")

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


def _run_calibration_mode_without_datatree(
    calibration: "Calibration",
    processor: Processor,
    with_buckets_separated: bool,
) -> None:
    """Run a 'Calibration' pipeline."""
    logging.info("Mode: Calibration")

    # Create an output folder
    outputs: Optional[CalibrationOutputs] = calibration.outputs
    if outputs:
        outputs.create_output_folder()

    # TODO: Improve this
    calibration.run_calibration(
        processor=processor,
        output_dir=outputs.current_output_folder if outputs else None,
        with_inherited_coords=with_buckets_separated,
    )


def _run_calibration_mode(
    calibration: "Calibration",
    processor: Processor,
    with_inherited_coords: bool,
) -> "DataTree":
    """Run a 'Calibration' pipeline.

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

    # Create an output folder
    outputs: Optional[CalibrationOutputs] = calibration.outputs
    if outputs:
        outputs.create_output_folder()

    data_tree: "DataTree" = calibration.run_calibration(
        processor=processor,
        output_dir=outputs.current_output_folder if outputs else None,
        with_inherited_coords=with_inherited_coords,
    )

    return data_tree


def _run_observation_mode_without_datatree(
    observation: Observation,
    processor: Processor,
) -> None:
    logging.info("Mode: Observation")

    # Create an output folder
    outputs: Optional[ObservationOutputs] = observation.outputs
    if outputs:
        outputs.create_output_folder()

    observation.run_pipelines_without_datatree(processor=processor)


def _run_observation_mode(
    observation: Observation,
    processor: Processor,
    with_inherited_coords: bool,
) -> "DataTree":
    """Run the observation mode."""
    logging.info("Mode: Observation")

    # Create an output folder (if needed)
    outputs: Optional[ObservationOutputs] = observation.outputs
    if outputs:
        outputs.create_output_folder()

    # Run the observation mode
    result: "DataTree" = observation.run_pipelines(
        processor=processor,
        with_inherited_coords=with_inherited_coords,
    )

    # TODO: Fix this. See issue #723
    if outputs and outputs.save_observation_data:
        raise NotImplementedError
    #     observation_outputs.save_observation_datasets(
    #         result=result, mode=observation.parameter_mode
    #     )

    return result


def run_mode(
    mode: Union[Exposure, Observation, "Calibration"],
    detector: Detector,
    pipeline: DetectionPipeline,
    override_dct: Optional[Mapping[str, Any]] = None,
    debug: bool = False,
    with_inherited_coords: bool = False,
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
    override_dct: dict, optional
        A dictionary of parameter(s) to override during processing.
    debug : bool, default: False
        Add all intermediate steps into the results as a ``DataTree``. This mode is used for debugging.
    with_inherited_coords : bool, default: False
        Return the results a DataTree with better hierarchical format. This parameter is provisional.

    Notes
    -----
    Parameter ``debug`` and ``with_hiearchical_format`` are not (yet) stable and may change in the future.

    Returns
    -------
    DataTree

    Raises
    ------
    TypeError
        Raised if the ``mode`` is not valid.

    NotImplementedError
        Raised if parameter ``debug`` is activated and `mode` is not an ``Exposure`` object.

    Examples
    --------
     Run an 'Exposure' pipeline

    >>> import pyxel
    >>> config = pyxel.load("exposure_configuration.yaml")
    >>> data_tree = pyxel.run_mode(
    ...     mode=config.exposure,
    ...     detector=config.detector,
    ...     pipeline=config.pipeline,
    ...     with_inherited_coords=True,  # with the new 'provisional' parameter
    ...     override={  # optional
    ...         "exposure.outputs.output_folder": "new_folder",
    ...         "pipeline.photon_collection.load_image.arguments.image_file": "new_image.fits",
    ...     },
    ... )
    >>> data_tree
    <xarray.DataTree>
    Group: /
    │   Dimensions: ()
    │   Data variables:
    │       *empty*
    │   Attributes:
    │       pyxel version:  2.4.1+56.ga760893c.dirty
    │       running mode:   Exposure
    ├── Group: /bucket
    │   │   Dimensions:  (time: 54, y: 100, x: 100)
    │   │   Coordinates:
    │   │     * time     (time) float64 0.02 0.06 0.12 0.2 0.3 ... 113.0 117.8 122.7 127.7
    │   │     * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
    │   │     * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
    │   │   Data variables:
    │   │       photon   (time, y, x) float64 4MB 85.0 120.0 109.0 ... 2.533e+04 2.51e+04
    │   │       charge   (time, y, x) float64 4MB 201.0 196.0 202.0 ... 2.543e+04 2.52e+04
    │   │       pixel    (time, y, x) float64 4MB 77.38 110.0 99.09 ... 2.406e+04 2.406e+04
    │   │       signal   (time, y, x) float64 4MB 0.0009377 0.001322 0.00133 ... 0.2968 0.2968
    │   │       image    (time, y, x) float64 4MB 16.0 22.0 22.0 ... 4.863e+03 4.863e+03
    │   └── Group: /bucket/scene
    │       └── Group: /bucket/scene/list
    │           └── Group: /bucket/scene/list/0
    │                   Dimensions:     (ref: 345, wavelength: 343)
    │                   Coordinates:
    │                     * ref         (ref) int64 0 1 2 3 4 5 6 7 ... 337 338 339 340 341 342 343 344
    │                     * wavelength  (wavelength) float64 336.0 338.0 340.0 ... 1.018e+03 1.02e+03
    │                   Data variables:
    │                       x           (ref) float64 3KB 2.057e+05 2.058e+05 ... 2.031e+05 2.03e+05
    │                       y           (ref) float64 3KB 8.575e+04 8.58e+04 ... 8.795e+04 8.807e+04
    │                       weight      (ref) float64 3KB 11.49 14.13 15.22 14.56 ... 15.21 11.51 8.727
    │                       flux        (ref, wavelength) 1MB float64 0.03769 0.04137 ... 1.813 1.896
    └── Group: /data
        ├── Group: /data/mean_variance
        │   └── Group: /data/mean_variance/image
        │           Dimensions:   (mean: 54)
        │           Coordinates:
        │             * mean      (mean) float64 19.64 38.7 57.77 ... 4.586e+03 4.682e+03 4.777e+03
        │           Data variables:
        │               variance  (mean) float64 432B 5.893 10.36 15.13 ... 1.235e+04 1.297e+04 1.342e+04
        └── Group: /data/statistics
            └── Group: /data/statistics/pixel
                    Dimensions:  (time: 54)
                    Coordinates:
                      * time     (time) float64 0.02 0.06 0.12 0.2 0.3 ... 113.0 117.8 122.7 127.7
                    Data variables:
                        var      (time) float64 432B 92.4 197.8 317.2 ... 3.027e+05 3.175e+05 3.286e+05
                        mean     (time) float64 432B 94.64 189.1 283.5 ... 2.269e+04 2.316e+04 2.363e+04
                        min      (time) float64 432B 63.39 134.9 220.3 ... 2.135e+04 2.193e+04 2.24e+04
                        max      (time) float64 432B 134.8 248.1 359.7 ... 2.522e+04 2.569e+04 2.64e+04
                        count    (time) float64 432B 1e+04 1e+04 1e+04 1e+04 ... 1e+04 1e+04 1e+04 1e+04

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
    ...     debug=True,
    ... )
    >>> results["/intermediate"]
    DataTree('intermediate', parent="data")
    │   Dimensions:  ()
    │   Data variables:
    │       *empty*
    │   Attributes:
    │       long_name:  Store all intermediate results modified along a pipeline
    └── DataTree('time_idx_0')
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

    # Ensure debug mode is only used with Exposure mode.
    if debug and not isinstance(mode, Exposure):
        raise NotImplementedError(
            "Parameter 'debug' is only implemented for 'Exposure' mode."
        )

    # Initialize the Processor object with the detector and pipeline.
    if isinstance(mode, Observation):
        processor = Processor(
            detector=detector,
            pipeline=pipeline,
            observation_mode=mode,  # TODO: See #836
        )
    else:
        processor = Processor(detector=detector, pipeline=pipeline)

    # Apply any overrides provided in the 'override_dct' to adjust processor settings.
    if override_dct is not None:
        apply_overrides(
            overrides=override_dct,
            processor=processor,
            mode=mode,
        )

    # Execute the appropriate processing function based on the mode type.
    if isinstance(mode, Exposure):
        data_tree = _run_exposure_mode(
            exposure=mode,
            processor=processor,
            debug=debug,
            with_inherited_coords=with_inherited_coords,
        )

    elif isinstance(mode, Observation):
        data_tree = _run_observation_mode(
            observation=mode,
            processor=processor,
            with_inherited_coords=with_inherited_coords,
        )

    else:
        # Late import.
        # Importing 'Calibration' can take up to 3 s !
        from pyxel.calibration import Calibration

        if isinstance(mode, Calibration):
            data_tree = _run_calibration_mode(
                calibration=mode,
                processor=processor,
                with_inherited_coords=with_inherited_coords,
            )
        else:
            raise TypeError("Please provide a valid simulation mode !")

    return data_tree


def output_directory(configuration: Configuration) -> Optional[Path]:
    """Return the output directory from the configuration.

    Parameters
    ----------
    configuration

    Returns
    -------
    output_dir
    """
    outputs: Union[
        "ExposureOutputs", "ObservationOutputs", "CalibrationOutputs", None
    ] = configuration.running_mode.outputs
    if outputs:
        return outputs.current_output_folder

    return None


def run(
    input_filename: Union[str, Path],
    override: Optional[Sequence[str]] = None,
    random_seed: Optional[int] = None,
) -> None:
    """Run a YAML configuration file.

    For more information, see :ref:`running_modes`.

    Parameters
    ----------
    input_filename : str or Path
    override : list of str
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

    pipeline: DetectionPipeline = configuration.pipeline
    detector: Union[CCD, CMOS, MKID, APD] = configuration.detector
    running_mode: Union[Exposure, Observation, "Calibration"] = (
        configuration.running_mode
    )

    # Extract the parameters to override
    override_dct: dict[str, Any] = {}
    if override is not None:
        for element in override:
            key, value = element.split("=")
            override_dct[key] = value

    processor = Processor(detector=detector, pipeline=pipeline)
    if override_dct is not None:
        apply_overrides(
            overrides=override_dct,
            processor=processor,
            mode=running_mode,
        )

    if isinstance(running_mode, Exposure):
        _run_exposure_mode_without_datatree(
            exposure=running_mode,
            processor=processor,
        )

    elif isinstance(running_mode, Observation):
        _run_observation_mode_without_datatree(
            observation=running_mode,
            processor=processor,
        )

    else:
        # Late import.
        # Importing 'Calibration' can take up to 3 s !
        from pyxel.calibration import Calibration

        if isinstance(running_mode, Calibration):
            _run_calibration_mode_without_datatree(
                calibration=running_mode,
                processor=processor,
                with_buckets_separated=False,
            )
        else:
            raise TypeError("Please provide a valid simulation mode !")

    output_dir: Optional[Path] = output_directory(configuration)

    # TODO: Fix this, see issue #728
    if output_dir:
        copy_config_file(input_filename=input_filename, output_dir=output_dir)

    logging.info("Pipeline completed.")
    logging.info("Running time: %.3f seconds", (time.time() - start_time))
    # Closing the logger in order to be able to move the file in the output dir
    logging.shutdown()

    if output_dir:
        outputs.save_log_file(output_dir)

    # Late import to speedup start-up time
    from matplotlib import pyplot as plt

    plt.close()


# TODO: Use ExceptionGroup
# TODO: Add unit tests
def apply_overrides(
    overrides: Mapping[str, Any],
    processor: Processor,
    mode: Union[Exposure, Observation, "Calibration"],
) -> None:
    """Override attributes to a specified processor / running_mode.

    Parameters
    ----------
    overrides : Mapping[str, Any]
        A dictionary containing the override key(s) and value(s) to be applied.
    processor
    mode

    Notes
    -----
    'processor' and 'mode' are modified !

    Raises
    ------
    AttributeError
        If an attribute specified in the overrides does not exist in the given mode.

    Examples
    --------
    >>> overrides = {
    ...     "observation.outputs.output_folder": "my_folder",
    ...     "pipeline.photon_collection.load_image.arguments.image_file": "image.fits",
    ... }
    >>> apply_overrides(overrides=overrides, processor=processor, mode=mode)
    """
    for key, value in overrides.items():
        # Check if 'key' is specified for a running mode (exposure, observation or calibration)
        if (
            key.startswith("exposure.")
            or key.startswith("observation.")
            or key.startswith("calibration.")
        ):
            # Modify 'key' and apply it to 'running_mode'
            new_key: str = (
                key.removeprefix("exposure.")
                .removeprefix("observation.")
                .removeprefix("calibration.")
            )

            obj, att = _get_obj_att(obj=mode, key=new_key)
            if hasattr(obj, att):
                setattr(obj, att, value)
            else:
                raise AttributeError(f"Object {mode!r} has no attribute {new_key!r}")

        else:
            processor.set(key=key, value=value)


# TODO: Add an option to display colors ?
@click.group()
@click.version_option(
    version=version
    + f"\nPython ({platform.python_implementation()}) {platform.python_version()}"
)
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
@click.argument("model_name", type=str, required=False)
def create_new_model(model_name: Optional[str]):
    """Create a new model.

    Use: arg1/arg2. Create a new module in ``pyxel/models/arg1/arg2`` using a template
    (``pyxel/templates/MODELTEMPLATE.py``)
    """
    if model_name is None:
        create_model_to_console()
    else:
        create_model(newmodel=model_name)


@main.command(name="run")
@click.argument("config", type=click.Path(exists=True))
@click.option(
    "--override",
    multiple=True,
    help="""
    Override entries from the YAML configuration file.
    This parameter can be repeated.\f
    Example:\f
    --override exposure.outputs.output_folder=new_folder""",
)
@click.option(
    "-v",
    "--verbosity",
    count=True,
    show_default=True,
    help="Increase output verbosity (-v/-vv/-vvv)",
)
def run_config(config: str, override: Sequence[str], verbosity: int):
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

    run(input_filename=config, override=override)


if __name__ == "__main__":
    main()
