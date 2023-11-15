#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Observation class and functions."""

import logging
from collections import defaultdict
from collections.abc import Sequence
from typing import TYPE_CHECKING, Optional, Union

import numpy as np
import xarray as xr
from datatree import DataTree
from tqdm.auto import tqdm

from pyxel import __version__
from pyxel.data_structure import Charge, Image, Photon, Pixel, Scene, Signal
from pyxel.pipelines import Processor, ResultId, get_result_id, result_keys
from pyxel.util import set_random_seed

if TYPE_CHECKING:
    from pyxel.detectors import Detector
    from pyxel.exposure import Readout
    from pyxel.outputs import CalibrationOutputs, ExposureOutputs, ObservationOutputs


class Exposure:
    """TBW."""

    def __init__(
        self,
        outputs: "ExposureOutputs",
        readout: "Readout",
        result_type: str = "all",
        pipeline_seed: Optional[int] = None,
    ):
        self.outputs = outputs
        self.readout = readout
        self._result_type: ResultId = get_result_id(result_type)
        self._pipeline_seed = pipeline_seed

    def __repr__(self) -> str:
        cls_name: str = self.__class__.__name__
        return f"{cls_name}<outputs={self.outputs!r}>"

    @property
    def result_type(self) -> ResultId:
        """TBW."""
        return self._result_type

    @result_type.setter
    def result_type(self, value: ResultId) -> None:
        """TBW."""
        self._result_type = value

    @property
    def pipeline_seed(self) -> Optional[int]:
        """TBW."""
        return self._pipeline_seed

    @pipeline_seed.setter
    def pipeline_seed(self, value: Optional[int]) -> None:
        """TBW."""
        self._pipeline_seed = value

    # TODO: This function will be deprecated
    def run_exposure(self, processor: Processor) -> "xr.Dataset":
        """Run an observation pipeline.

        Parameters
        ----------
        processor : Processor

        Returns
        -------
        Dataset
        """
        progressbar = self.readout._num_steps != 1
        y = range(processor.detector.geometry.row)
        x = range(processor.detector.geometry.col)
        times = self.readout.times

        # Unpure changing of processor
        _ = run_exposure_pipeline(
            processor=processor,
            readout=self.readout,
            outputs=self.outputs,
            progressbar=progressbar,
            result_type=self.result_type,
            pipeline_seed=self.pipeline_seed,
        )

        ds: xr.Dataset = processor.result_to_dataset(
            x=x,
            y=y,
            times=times,
            result_type=self.result_type,
        )

        ds.attrs.update({"running mode": "Exposure"})

        return ds

    def run_exposure_new(
        self,
        processor: Processor,
        with_intermediate_steps: bool,
    ) -> DataTree:
        """Run an observation pipeline.

        Parameters
        ----------
        processor : Processor
        with_intermediate_steps : bool

        Returns
        -------
        DataTree
        """
        progressbar = self.readout._num_steps != 1

        # Unpure changing of processor
        data_tree: DataTree = run_pipeline(
            processor=processor,
            readout=self.readout,
            outputs=self.outputs,
            progressbar=progressbar,
            result_type=self.result_type,
            pipeline_seed=self.pipeline_seed,
            with_intermediate_steps=with_intermediate_steps,
        )

        data_tree.attrs["running mode"] = "Exposure"

        return data_tree


# TODO: This function will be deprecated
def run_exposure_pipeline(
    processor: Processor,
    readout: "Readout",
    outputs: Union[
        "CalibrationOutputs", "ObservationOutputs", "ExposureOutputs", None
    ] = None,
    progressbar: bool = False,
    result_type: ResultId = ResultId("all"),  # noqa: B008
    pipeline_seed: Optional[int] = None,
) -> Processor:
    """Run standalone exposure pipeline.

    Parameters
    ----------
    pipeline_seed: int
        Random seed for the pipeline.
    result_type: ResultId
    processor: Processor
    readout: Readout
    outputs: DynamicOutputs
        Sampling outputs.
    progressbar: bool
        Sets visibility of progress bar.

    Returns
    -------
    processor: Processor
    """
    # if isinstance(detector, CCD):
    #    dynamic.non_destructive_readout = False

    with set_random_seed(seed=pipeline_seed):
        num_steps = readout._num_steps
        readout._times[-1]
        readout.time_step_it()

        detector = processor.detector

        detector.set_readout(
            times=readout.times,
            start_time=readout.start_time,
            non_destructive=readout.non_destructive,
        )

        # The detector should be reset before exposure
        detector.empty()

        if progressbar:
            pbar = tqdm(total=num_steps, desc="Readout time: ")

        keys = result_keys(result_type)

        unstacked_result: dict[str, list] = defaultdict(list)
        i: int
        time: float
        step: float
        for i, (time, step) in enumerate(
            zip(detector.readout_properties.times, detector.readout_properties.steps)
        ):
            detector.time = time
            detector.time_step = step
            detector.pipeline_count = i

            logging.info("time = %.3f s", time)

            if detector.non_destructive_readout:
                empty_all = False
            else:
                empty_all = True

            detector.empty(empty_all)

            processor.run_pipeline()

            if outputs and detector.read_out:
                outputs.save_to_file(processor)

            for key in keys:
                if key in ("data", "scene"):
                    continue

                obj: Union[Scene, Photon, Pixel, Image, Signal, Charge] = getattr(
                    detector, key
                )

                # TODO: Is this necessary ?
                if not isinstance(obj, (Photon, Pixel, Image, Signal, Charge)):
                    raise TypeError(
                        f"Wrong type from attribute 'detector.{key}'. Type: {type(obj)!r}"
                    )

                if obj._array is not None:
                    data_arr: np.ndarray = np.array(obj)
                    unstacked_result[key].append(data_arr)

            if progressbar:
                pbar.update(1)

        # TODO: Refactor '.result'. See #524
        processor.result = {
            key: np.stack(value)
            for key, value in unstacked_result.items()
            if key != "data"
        }

        if progressbar:
            pbar.close()

    return processor


def _extract_datatree(detector: "Detector", keys: Sequence[ResultId]) -> DataTree:
    """Extract data from a detector object into a `DataTree`.

    Parameters
    ----------
    detector : Detector
    keys:
        Bucket(s) to extract (e.g. ["photon", "charge", "pixel", "signal", "image", "data"])

    Returns
    -------
    DataTree

    Notes
    -----
    This function is used internally.

    Examples
    --------
    >>> _extract_datatree(
    ...     detector=detector,
    ...     keys=["photon", "charge", "pixel", "signal", "image", "data"],
    ... )
    DataTree('None', parent=None)
        Dimensions:  (time: 1, y: 100, x: 100)
        Coordinates:
          * time     (time) float64 1.0
          * y        (y) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
          * x        (x) int64 0 1 2 3 4 5 6 7 8 9 10 ... 90 91 92 93 94 95 96 97 98 99
        Data variables:
            photon   (time, y, x) float64 1.515e+04 1.592e+04 ... 1.621e+04 1.621e+04
            charge   (time, y, x) float64 1.515e+04 1.592e+04 ... 1.621e+04 1.621e+04
            pixel    (time, y, x) float64 1.515e+04 1.592e+04 ... 1.621e+04 1.621e+04
            signal   (time, y, x) float64 0.04545 0.04776 0.04634 ... 0.04862 0.04862
            image    (time, y, x) uint32 298 314 304 304 304 314 ... 339 339 328 319 319
    """
    # Get current absolute time
    absolute_time = xr.DataArray(
        [detector.absolute_time],
        dims=["time"],
        attrs={"units": "s"},
    )

    dataset: xr.Dataset = xr.Dataset()

    key: ResultId
    for key in keys:
        if key.startswith("data") or key.startswith("scene"):
            continue

        obj: Union[Photon, Pixel, Image, Signal, Charge] = getattr(detector, key)

        # TODO: Is this necessary ?
        if not isinstance(obj, (Photon, Pixel, Image, Signal, Charge)):
            raise TypeError(
                f"Wrong type from attribute 'detector.{key}'. Type: {type(obj)!r}"
            )

        data_array: xr.DataArray = obj.to_xarray().expand_dims(time=absolute_time)
        data_array.name = "value"

        dataset[key] = data_array

    return DataTree(dataset)


def run_pipeline(
    processor: Processor,
    readout: "Readout",
    outputs: Union[
        "CalibrationOutputs", "ObservationOutputs", "ExposureOutputs", None
    ] = None,
    progressbar: bool = False,
    result_type: ResultId = ResultId("all"),  # noqa: B008
    pipeline_seed: Optional[int] = None,
    with_intermediate_steps: bool = False,
) -> DataTree:
    """Run standalone exposure pipeline.

    Parameters
    ----------
    processor : Processor
    readout : Readout
    outputs : DynamicOutputs
        Sampling outputs.
    progressbar : bool
        Sets visibility of progress bar.
    result_type : ResultId
    pipeline_seed : int
        Random seed for the pipeline.
    with_intermediate_steps : bool

    Returns
    -------
    DataTree
    """
    # if isinstance(detector, CCD):
    #    dynamic.non_destructive_readout = False

    with set_random_seed(seed=pipeline_seed):
        detector = processor.detector

        detector.set_readout(
            times=readout.times,
            start_time=readout.start_time,
            non_destructive=readout.non_destructive,
        )

        # The detector should be reset before exposure
        detector.empty()

        if progressbar:
            pbar = tqdm(
                total=detector.readout_properties.num_steps, desc="Readout time: "
            )

        # Get attributes to extract from 'detector'
        # Example: keys = ['photon', 'charge', 'pixel', 'signal', 'image', 'data']
        keys: Sequence[ResultId] = result_keys(result_type)

        data_tree: DataTree = DataTree()

        i: int
        time: float
        step: float
        for i, (time, step) in enumerate(
            zip(detector.readout_properties.times, detector.readout_properties.steps)
        ):
            detector.readout_properties.time = time
            detector.readout_properties.time_step = step
            detector.readout_properties.pipeline_count = i

            logging.info("time = %.3f s", time)

            # Empty detector (if needed)
            is_destructive_readout: bool = not detector.non_destructive_readout
            detector.empty(is_destructive_readout)

            # Run one pipeline
            processor.run_pipeline(with_intermediate_steps=with_intermediate_steps)

            # Save results in file(s) (if needed)
            if outputs and detector.read_out:
                outputs.save_to_file(processor)

            # Extract data from 'detector' into a 'DataTree'
            partial_datatree: DataTree = _extract_datatree(detector=detector, keys=keys)

            # Concatenate all 'partialtree'
            if data_tree.is_empty:
                data_tree = partial_datatree
            else:
                data_tree = data_tree.combine_first(partial_datatree)

                # Fix dtype of container 'image'. See #652
                image_dtype: np.dtype = data_tree["image"].dtype
                exp_dtype: np.dtype = detector.image.dtype

                if image_dtype != exp_dtype:
                    new_image: xr.DataArray = data_tree["image"].astype(dtype=exp_dtype)
                    data_tree["image"] = new_image

            if progressbar:
                pbar.update(1)

        if with_intermediate_steps:
            # Remove temporary data_tree '/intermediate/last'
            datatree_intermediate: DataTree = detector.data["intermediate"]  # type: ignore
            del datatree_intermediate["last"]

        if "scene" in keys:
            data_tree["/scene"] = detector.scene.data

        if "data" in keys:
            data_tree["/data"] = detector.data

        data_tree.attrs["pyxel version"] = __version__

        if progressbar:
            pbar.close()

    return data_tree
