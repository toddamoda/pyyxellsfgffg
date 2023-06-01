#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

""":term:`CDM` model calibration with PYGMO.

https://esa.github.io/pagmo2/index.html
"""
import copy
import logging
import math
from collections.abc import Sequence
from copy import deepcopy
from numbers import Number
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, Union

import numpy as np
import pandas as pd
import xarray as xr
from dask.delayed import delayed
from numpy.typing import NDArray

from pyxel.calibration import (
    FitRange2D,
    FitRange3D,
    FittingCallable,
    ProblemSingleObjective,
    check_fit_ranges,
    read_data,
    read_datacubes,
)
from pyxel.exposure import run_pipeline
from pyxel.inputs import load_dataarray
from pyxel.observation import ParameterValues
from pyxel.pipelines import Processor, ResultId

if TYPE_CHECKING:
    from datatree import DataTree
    from numpy.typing import ArrayLike

    from pyxel.exposure import Readout


def build_processors(
    processor: Processor,
    arguments: Sequence[ParameterValues],
) -> Sequence[Processor]:
    max_val, min_val = 0, 1000
    for arg in arguments:
        min_val = min(min_val, len(arg.values))
        max_val = max(max_val, len(arg.values))

    if min_val != max_val:
        logging.warning(
            'The "result_input_arguments" value lists have different lengths! '
            "Some values will be ignored."
        )

    processors: list[Processor] = []
    for i in range(min_val):
        new_processor: Processor = deepcopy(processor)

        step: ParameterValues
        for step in arguments:
            assert step.values != "_"

            value: Union[Literal["_"], str, Number] = step.values[i]

            step.current = value
            new_processor.set(key=step.key, value=step.current)

        processors.append(new_processor)

    return processors


class ModelFittingDataTree(ProblemSingleObjective):
    """Pygmo problem class to fit data with any model in Pyxel."""

    def __init__(
        self,
        processor: Processor,
        variables: Sequence[ParameterValues],
        readout: "Readout",
        simulation_output: ResultId,
        generations: int,
        population_size: int,
        fitness_func: FittingCallable,
        file_path: Path,
        target_fit_range: Union[FitRange2D, FitRange3D],
        out_fit_range: FitRange3D,
        target_filenames: Sequence[Path],
        input_arguments: Optional[Sequence[ParameterValues]] = None,
        weights: Optional[Sequence[float]] = None,
        weights_from_file: Optional[Sequence[Path]] = None,
        pipeline_seed: Optional[int] = None,
    ):
        self._variables: Sequence[ParameterValues] = variables

        self.generations: int = generations
        self.pop: int = population_size
        self.readout: Readout = readout

        self.weighting: Optional[np.ndarray] = None
        self.weighting_from_file: Optional[Sequence[np.ndarray]] = None
        self.fitness_func: FittingCallable = fitness_func
        self.sim_output: ResultId = simulation_output

        self.file_path: Path = file_path
        self.pipeline_seed: Optional[int] = pipeline_seed

        lower_boundaries, upper_boundaries = self._set_bound()
        self._lower_boundaries: Sequence[float] = lower_boundaries
        self._upper_boundaries: Sequence[float] = upper_boundaries

        if not input_arguments:
            processors: Sequence[Processor] = [deepcopy(processor)]
        else:
            processors = build_processors(
                processor=processor,
                arguments=input_arguments,
            )
        self.param_processor_list: Sequence[Processor] = processors

        num_parameters: int = 0

        var: ParameterValues
        for var in self._variables:
            if isinstance(var.values, list):
                b = len(var.values)
            else:
                b = 1

            num_parameters += b
        self.champion_f_list: np.ndarray = np.zeros((1, 1))
        self.champion_x_list: np.ndarray = np.zeros((1, num_parameters))

        if not simulation_output.startswith("data"):
            if self.readout.time_domain_simulation:
                # Target(s) is/are 3D array(s) of dimensions: 'readout_time', 'y', 'x'
                target_list_3d: Sequence[np.ndarray] = read_datacubes(
                    filenames=target_filenames
                )
                targets = xr.DataArray(
                    target_list_3d,
                    dims=["processor", "readout_time", "y", "x"],
                )

                times = len(targets["readout_time"])
                rows = len(targets["y"])
                cols = len(targets["x"])

                # times, rows, cols = target_list_3d[0].shape
                check_fit_ranges(
                    target_fit_range=target_fit_range,
                    out_fit_range=out_fit_range,
                    rows=rows,
                    cols=cols,
                    readout_times=times,
                )

            else:
                # Target(s) is/are 2D array(s) of dimensions: 'y', 'x'
                target_list_2d: Sequence[np.ndarray] = read_data(
                    filenames=target_filenames
                )
                targets = xr.DataArray(target_list_2d, dims=["processor", "y", "x"])

                rows = len(targets["y"])
                cols = len(targets["x"])

                check_fit_ranges(
                    target_fit_range=target_fit_range,
                    out_fit_range=out_fit_range,
                    rows=rows,
                    cols=cols,
                )
                self._configure_weights(
                    weights=weights,
                    weights_from_file=weights_from_file,
                )

            self.targ_fit_range: Union[FitRange2D, FitRange3D, None] = target_fit_range
            self.sim_fit_range: Optional[FitRange3D] = out_fit_range
            self.all_target_data: xr.DataArray = targets.sel(
                indexers=target_fit_range.to_dict()
            )

        else:
            # Target(s) is/are arrays(s) of unknown number of dimensions.
            # For this reason the file(s) are directly read as 'DataArray' object(s).
            targets_list: Sequence["xr.DataArray"] = [
                load_dataarray(filename) for filename in target_filenames
            ]
            targets = xr.concat(targets_list, dim="processor")

            self.targ_fit_range = None
            self.sim_fit_range = None
            self.all_target_data = targets

    def get_bounds(self) -> tuple[Sequence[float], Sequence[float]]:
        """Get the box bounds of the problem (lower_boundary, upper_boundary).

        It also implicitly defines the dimension of the problem.

        Returns
        -------
        tuple of lower boundaries and upper boundaries
        """
        return self._lower_boundaries, self._upper_boundaries

    def _configure_weights(
        self,
        weights: Optional[Sequence[float]] = None,
        weights_from_file: Optional[Sequence[Path]] = None,
    ) -> None:
        """TBW.

        Parameters
        ----------
        weights
        weights_from_file
        """
        if weights_from_file is not None:
            assert self.targ_fit_range is not None

            if self.readout.time_domain_simulation:
                wf = read_datacubes(weights_from_file)
                self.weighting_from_file = [
                    weight_array[self.targ_fit_range.to_slices()] for weight_array in wf
                ]
            else:
                wf = read_data(weights_from_file)
                self.weighting_from_file = [
                    weight_array[self.targ_fit_range.to_slices()] for weight_array in wf
                ]
        elif weights is not None:
            self.weighting = np.array(weights)

    def _set_bound(self) -> tuple[Sequence[float], Sequence[float]]:
        lbd: list[float] = []
        ubd: list[float] = []

        var: ParameterValues
        for var in self._variables:
            assert var.boundaries is not None  # TODO: Fix this

            if var.values == "_":
                assert var.boundaries.shape == (2,)  # TODO: Fix this

                low_val: float
                high_val: float
                low_val, high_val = var.boundaries

                if var.logarithmic:
                    low_val = math.log10(low_val)
                    high_val = math.log10(high_val)

                lbd += [low_val]
                ubd += [high_val]

            elif isinstance(var.values, Sequence) and all(
                x == "_" for x in var.values[:]
            ):
                if var.boundaries.ndim == 1:
                    low_val, high_val = var.boundaries

                    low_values: NDArray[np.float_] = np.array(
                        [low_val] * len(var.values)
                    )
                    high_values: NDArray[np.float_] = np.array(
                        [high_val] * len(var.values)
                    )

                elif var.boundaries.ndim == 2:
                    low_values = var.boundaries[:, 0]
                    high_values = var.boundaries[:, 1]
                else:
                    raise NotImplementedError

                if var.logarithmic:
                    low_values = np.log10(low_values)
                    high_values = np.log10(high_values)

                lbd += low_values.tolist()
                ubd += high_values.tolist()

            else:
                raise ValueError(
                    'Character "_" (or a list of it) should be used to '
                    "indicate variables need to be calibrated"
                )

        return lbd, ubd

    def get_simulated_data(self, data: "DataTree") -> "xr.DataArray":
        """Extract 2D data from a processor."""
        import xarray as xr

        if self.sim_output in ("image", "signal", "pixel"):
            simulated_data = data[f"bucket/{self.sim_output}"]
        elif self.sim_output.startswith("data"):
            simulated_data = data[self.sim_output]
        else:
            raise NotImplementedError(
                f"Simulation mode: {self.sim_output!r} not implemented"
            )

        if not isinstance(simulated_data, xr.DataArray):
            raise TypeError("Expected a 'DataArray'")

        if self.sim_fit_range is not None:
            simulated_data = simulated_data.sel(indexers=self.sim_fit_range.to_dict())

        return simulated_data

    def _calculate_fitness(
        self,
        simulated_data: "xr.DataArray",
        target_data: "xr.DataArray",
        weighting: Optional[np.ndarray] = None,
    ) -> float:
        if self.sim_output.startswith("data"):
            assert simulated_data.ndim == target_data.ndim

            # Create 'simulated_renamed' with the same dimensions as 'target_data'
            renamed_dimensions = dict(zip(simulated_data.dims, target_data.dims))
            simulated_renamed: xr.DataArray = simulated_data.rename(renamed_dimensions)

            # 'simulated_interpolated' has the same coordinates as 'target_data'
            simulated_interpolated = simulated_renamed.interp_like(target_data)

            simulated_2d = np.array(simulated_interpolated, dtype=float)

        else:
            simulated_2d = np.array(simulated_data, dtype=float)

        target_2d = np.array(target_data, dtype=float)

        if weighting is not None:
            factor = weighting
        else:
            factor = np.ones_like(target_2d)

        weighting_2d = np.array(factor, dtype=float)

        fitness: float = self.fitness_func(
            simulated=simulated_2d,
            target=target_2d,
            weighting=weighting_2d,
        )

        return fitness

    # TODO: If possible, use 'numba' for this method
    def fitness(self, decision_vector_1d: np.ndarray) -> Sequence[float]:
        """Call the fitness function, elements of parameter array could be logarithmic values.

        Parameters
        ----------
        decision_vector_1d : array_like
            A 1d decision vector.

        Returns
        -------
        sequence
            The fitness of the input decision vector (concatenating the objectives,
            the equality and the inequality constraints)
        """
        # TODO: Fix this
        if self.pop is None:
            raise NotImplementedError("'pop' is not initialized.")

        try:
            # TODO: Use directory 'logging.'
            logger = logging.getLogger("pyxel")
            prev_log_level = logger.getEffectiveLevel()

            parameter_1d = self.convert_to_parameters(decision_vector_1d)
            # TODO: deepcopy is not needed. Check this
            processor_list: Sequence[Processor] = self.param_processor_list

            overall_fitness: float = 0.0
            for i, (processor, target_data) in enumerate(
                zip(processor_list, self.all_target_data)
            ):
                processor = self.update_processor(
                    parameter=parameter_1d, processor=processor
                )

                logger.setLevel(logging.WARNING)

                data_tree: "DataTree" = run_pipeline(
                    processor=processor,
                    readout=self.readout,
                    pipeline_seed=self.pipeline_seed,
                )

                logger.setLevel(prev_log_level)

                simulated_data: "xr.DataArray" = self.get_simulated_data(data=data_tree)

                weighting: Optional[np.ndarray] = None

                if self.weighting is not None:
                    weighting = np.full(
                        shape=(
                            processor.detector.geometry.row,
                            processor.detector.geometry.col,
                        ),
                        fill_value=self.weighting[i],
                    )
                elif self.weighting_from_file is not None:
                    weighting = self.weighting_from_file[i]

                overall_fitness += self._calculate_fitness(
                    simulated_data=simulated_data,
                    target_data=target_data,
                    weighting=weighting,
                )

        except Exception:
            logging.exception(
                "Catch an exception in 'fitness' for ModelFitting: %r.", self
            )
            raise

        return [overall_fitness]

    def convert_to_parameters(self, decisions_vector: "ArrayLike") -> np.ndarray:
        """Convert a decision version from Pygmo2 to parameters.

        Parameters
        ----------
        decisions_vector : array_like
            It could a 1D or 2D array.

        Returns
        -------
        array_like
            Parameters
        """
        parameters = np.array(decisions_vector)

        a = 0
        for var in self._variables:
            b = 1
            if isinstance(var.values, list):
                b = len(var.values)
            if var.logarithmic:
                start = a
                stop = a + b
                parameters[..., start:stop] = np.power(10, parameters[..., start:stop])
            a += b

        return parameters

    def apply_parameters(
        self, processor: Processor, parameter: np.ndarray
    ) -> "DataTree":
        """Create a new ``Processor`` with new parameters."""
        new_processor = self.update_processor(parameter=parameter, processor=processor)

        data_tree: "DataTree" = run_pipeline(
            processor=new_processor,
            readout=self.readout,
            pipeline_seed=self.pipeline_seed,
        )

        return data_tree

    def apply_parameters_to_processors(
        self, parameters: "xr.DataArray"
    ) -> pd.DataFrame:
        """TBW."""
        assert "island" in parameters.dims
        assert "param_id" in parameters.dims

        lst = []
        for id_processor, processor in enumerate(self.param_processor_list):
            delayed_processor = delayed(processor)

            for idx_island, params_array in parameters.groupby("island"):
                params: np.ndarray = params_array.data  # type

                result_datatree: DataTree = delayed(self.apply_parameters)(
                    processor=delayed_processor, parameter=params
                )

                lst.append(
                    {
                        "island": idx_island,
                        "id_processor": id_processor,
                        "data_tree": result_datatree,
                    }
                )

        df = pd.DataFrame(lst).sort_values(["island", "id_processor"])

        return df

    def update_processor(
        self, parameter: np.ndarray, processor: Processor
    ) -> Processor:
        """TBW."""
        new_processor = copy.deepcopy(processor)
        a, b = 0, 0
        for var in self._variables:
            if var.values == "_":
                b = 1
                new_processor.set(key=var.key, value=parameter[a])
            elif isinstance(var.values, list):
                b = len(var.values)

                start = a
                stop = a + b
                new_processor.set(key=var.key, value=parameter[start:stop])
            a += b
        return new_processor
