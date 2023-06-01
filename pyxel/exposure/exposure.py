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
import operator
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Optional, Union

import numpy as np
import xarray as xr
from datatree import DataTree
from tqdm.auto import tqdm

from pyxel import __version__
from pyxel.data_structure import Charge, Image, Photon, Pixel, Signal
from pyxel.exposure import Readout
from pyxel.pipelines import Processor, ResultId, get_result_id, result_keys
from pyxel.util import set_random_seed

if TYPE_CHECKING:
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

    def run_exposure_new(self, processor: Processor) -> DataTree:
        """Run an observation pipeline.

        Parameters
        ----------
        processor : Processor

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
        ndreadout = readout.non_destructive
        times_linear = readout._times_linear
        start_time = readout._start_time
        end_time = readout._times[-1]
        time_step_it = readout.time_step_it()

        detector = processor.detector

        detector.set_readout(
            num_steps=num_steps,
            ndreadout=ndreadout,
            times_linear=times_linear,
            start_time=start_time,
            end_time=end_time,
        )
        # The detector should be reset before exposure
        detector.empty()

        if progressbar:
            pbar = tqdm(total=num_steps, desc="Readout time: ")

        keys = result_keys(result_type)

        unstacked_result: Mapping[str, list] = {key: [] for key in keys}

        i: int
        time: float
        step: float
        for i, (time, step) in enumerate(time_step_it):
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
                if key == "data":
                    continue

                unstacked_result[key].append(
                    np.array(operator.attrgetter(key)(detector))
                )

            if progressbar:
                pbar.update(1)

        # TODO: Refactor '.result'. See #524
        processor.result = {
            key: np.stack(unstacked_result[key]) for key in keys if key != "data"
        }

        if progressbar:
            pbar.close()

    return processor


def run_pipeline(
    processor: Processor,
    readout: "Readout",
    outputs: Union[
        "CalibrationOutputs", "ObservationOutputs", "ExposureOutputs", None
    ] = None,
    progressbar: bool = False,
    result_type: ResultId = ResultId("all"),  # noqa: B008
    pipeline_seed: Optional[int] = None,
) -> DataTree:
    """Run standalone exposure pipeline.

    Parameters
    ----------
    pipeline_seed : int
        Random seed for the pipeline.
    result_type : ResultId
    processor : Processor
    readout : Readout
    outputs : DynamicOutputs
        Sampling outputs.
    progressbar : bool
        Sets visibility of progress bar.

    Returns
    -------
    DataTree
    """
    # if isinstance(detector, CCD):
    #    dynamic.non_destructive_readout = False

    with set_random_seed(seed=pipeline_seed):
        num_steps = readout._num_steps
        ndreadout = readout.non_destructive
        times_linear = readout._times_linear
        start_time = readout._start_time
        end_time = readout._times[-1]
        time_step_it = readout.time_step_it()

        detector = processor.detector

        detector.set_readout(
            num_steps=num_steps,
            ndreadout=ndreadout,
            times_linear=times_linear,
            start_time=start_time,
            end_time=end_time,
        )
        # The detector should be reset before exposure
        detector.empty()

        if progressbar:
            pbar = tqdm(total=num_steps, desc="Readout time: ")

        keys: Sequence[ResultId] = result_keys(result_type)

        data_tree: DataTree = DataTree()

        i: int
        time: float
        step: float
        for i, (time, step) in enumerate(time_step_it):
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

            # Get current absolute time
            absolute_time = xr.DataArray(
                [detector.absolute_time],
                dims=["time"],
                attrs={"units": "s"},
            )

            partial_data_tree: DataTree = DataTree()

            key: ResultId
            for key in keys:
                if key.startswith("data"):
                    continue

                obj: Union[Photon, Pixel, Image, Signal, Charge] = getattr(
                    detector, key
                )

                if isinstance(obj, (Photon, Pixel, Image, Signal, Charge)):
                    data_array: xr.DataArray = obj.to_xarray().expand_dims(
                        time=absolute_time
                    )
                    data_array.name = "value"

                    partial_data_tree[f"/bucket/{key}"] = data_array
                else:
                    raise NotImplementedError

            if progressbar:
                pbar.update(1)

            if data_tree.get("bucket") is None:
                data_tree = partial_data_tree
            else:
                data_tree = data_tree.combine_first(partial_data_tree)

        if "data" in keys:
            data_tree["/data"] = detector.data

        data_tree.attrs["pyxel version"] = __version__

        if progressbar:
            pbar.close()

    return data_tree
