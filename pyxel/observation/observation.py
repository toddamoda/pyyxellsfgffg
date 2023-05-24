#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Parametric mode class and helper functions."""
import itertools
import logging
from collections import Counter
from collections.abc import Iterable, Iterator, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from functools import partial, reduce
from numbers import Number
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Literal,
    NamedTuple,
    Optional,
    Tuple,
    Union,
)

import dask.bag as db
import numpy as np
import pandas as pd
import toolz
from numpy.typing import ArrayLike
from tqdm.auto import tqdm

from pyxel.exposure import Readout, run_exposure_pipeline, run_pipeline
from pyxel.observation.parameter_values import ParameterType, ParameterValues
from pyxel.pipelines import ResultId, get_result_id
from pyxel.state import get_obj_att, get_value

if TYPE_CHECKING:
    import xarray as xr
    from datatree import DataTree

    from pyxel.outputs import ObservationOutputs
    from pyxel.pipelines import Processor


class ParameterMode(Enum):
    """Parameter mode class."""

    Product = "product"
    Sequential = "sequential"
    Custom = "custom"


class ObservationResult(NamedTuple):
    """Result class for observation class."""

    dataset: Union["xr.Dataset", dict[str, "xr.Dataset"]]
    parameters: "xr.Dataset"
    logs: "xr.Dataset"


@dataclass(frozen=True)
class ParameterItem:
    """Internal Parameter Item."""

    # TODO: Merge 'index' and 'parameters'
    index: tuple[int, ...]
    parameters: Mapping[str, Any]
    run_index: int


@dataclass(frozen=True)
class CustomParameterItem:
    """Internal Parameter Item."""

    # TODO: Merge 'index' and 'parameters'
    index: int
    parameters: Mapping[str, Any]
    run_index: int


def _get_short_name_with_model(name: str) -> str:
    _, _, model_name, _, param_name = name.split(".")

    return f"{model_name}.{param_name}"


def _get_final_short_name(name: str, param_type: ParameterType) -> str:
    if param_type == ParameterType.Simple:
        return name
    elif param_type == ParameterType.Multi:
        return _id(name)
    else:
        raise NotImplementedError


# TODO: This function will be deprecated (see #563)
def _get_short_dimension_names(types: Mapping[str, ParameterType]) -> Mapping[str, str]:
    # Create potential names for the dimensions
    potential_dim_names: dict[str, str] = {}
    for param_name, param_type in types.items():
        short_name: str = short(param_name)

        potential_dim_names[param_name] = _get_final_short_name(
            name=short_name, param_type=param_type
        )

    # Find possible duplicates
    count_dim_names: Mapping[str, int] = Counter(potential_dim_names.values())

    duplicate_dim_names: Sequence[str] = [
        name for name, freq in count_dim_names.items() if freq > 1
    ]

    if duplicate_dim_names:
        dim_names: dict[str, str] = {}
        for param_name, param_type in types.items():
            short_name = potential_dim_names[param_name]

            if short_name in duplicate_dim_names:
                new_short_name: str = _get_short_name_with_model(param_name)
                dim_names[param_name] = _get_final_short_name(
                    name=new_short_name, param_type=param_type
                )

            else:
                dim_names[param_name] = short_name

        return dim_names

    return potential_dim_names


# TODO: Add unit tests
def _get_short_dimension_names_new(
    types: Mapping[str, ParameterType]
) -> Mapping[str, str]:
    # Create potential names for the dimensions
    potential_dim_names: dict[str, str] = {}
    for param_name in types:
        short_name: str = short(param_name)

        potential_dim_names[param_name] = short_name

    # Find possible duplicates
    count_dim_names: Mapping[str, int] = Counter(potential_dim_names.values())

    duplicate_dim_names: Sequence[str] = [
        name for name, freq in count_dim_names.items() if freq > 1
    ]

    if duplicate_dim_names:
        dim_names: dict[str, str] = {}
        for param_name in types:
            short_name = potential_dim_names[param_name]

            if short_name in duplicate_dim_names:
                new_short_name: str = _get_short_name_with_model(param_name)
                dim_names[param_name] = new_short_name

            else:
                dim_names[param_name] = short_name

        return dim_names

    return potential_dim_names


class Observation:
    """Observation class."""

    def __init__(
        self,
        outputs: "ObservationOutputs",
        parameters: Sequence[ParameterValues],
        readout: Optional[Readout] = None,
        mode: Literal["product", "sequential", "custom"] = "product",
        from_file: Optional[str] = None,  # Note: Only For 'custom' mode
        column_range: Optional[tuple[int, int]] = None,  # Note: Only For 'custom' mode
        with_dask: bool = False,
        result_type: str = "all",
        pipeline_seed: Optional[int] = None,
    ):
        self.outputs = outputs
        self.readout: Readout = readout or Readout()
        self.parameter_mode: ParameterMode = ParameterMode(mode)
        self._parameters: Sequence[ParameterValues] = parameters

        # Specific to mode 'custom'
        self._custom_file: Optional[str] = from_file
        self._custom_data: Optional[pd.DataFrame] = None
        self._custom_columns: Optional[slice] = (
            slice(*column_range) if column_range else None
        )

        self.with_dask = with_dask
        self.parameter_types: dict[str, ParameterType] = {}
        self._result_type: ResultId = get_result_id(result_type)
        self._pipeline_seed = pipeline_seed

        if self.parameter_mode == ParameterMode.Custom:
            self._load_custom_parameters()

    def __repr__(self):
        cls_name: str = self.__class__.__name__
        return f"{cls_name}<mode={self.parameter_mode!s}>"

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
    def pipeline_seed(self, value: int) -> None:
        """TBW."""
        self._pipeline_seed = value

    @property
    def enabled_steps(self) -> Sequence[ParameterValues]:
        """Return a list of enabled ParameterValues."""
        out = [step for step in self._parameters if step.enabled]
        return out

    # TODO: is self._custom_data really needed?
    def _load_custom_parameters(self) -> None:
        """Load custom parameters from file."""
        from pyxel import load_table

        if self._custom_file is None:
            raise ValueError("File for custom parametric mode not specified!")

        # Read the file without forcing its data type
        all_data: pd.DataFrame = load_table(self._custom_file, dtype=None)
        filtered_data: pd.DataFrame = all_data.loc[:, self._custom_columns]

        self._custom_data = filtered_data

    def _custom_parameters(
        self,
    ) -> Iterator[
        tuple[
            int,
            dict[str, Union[Number, str, Sequence[Union[Number, str]]]],
        ]
    ]:
        """Generate custom mode parameters based on input file.

        Yields
        ------
        index: int
        parameter_dict: dict
        """
        if not isinstance(self._custom_data, pd.DataFrame):
            raise TypeError("Custom parameters not loaded from file.")

        index: int
        row_serie: pd.Series
        for index, row_serie in self._custom_data.iterrows():
            row: Sequence[Union[Number, str]] = row_serie.to_list()

            i: int = 0
            parameter_dict: dict[
                str, Union[Number, str, Sequence[Union[Number, str]]]
            ] = {}
            for step in self.enabled_steps:
                key: str = step.key

                # TODO: this is confusing code. Fix this.
                #       Furthermore 'step.values' should be a `List[int, float]` and not a `str`
                if step.values == "_":
                    parameter_dict[key] = row[i]

                elif isinstance(step.values, Sequence):
                    values: np.ndarray = np.array(step.values)
                    values_flattened = values.flatten()

                    # TODO: find a way to remove the ignore
                    if not all(x == "_" for x in values_flattened):
                        raise ValueError(
                            'Only "_" characters (or a list of them) should be used to '
                            "indicate parameters updated from file in custom mode"
                        )

                    value: Sequence[Union[Number, str]] = row[
                        i : i + len(values_flattened)
                    ]
                    assert len(value) == len(step.values)

                    parameter_dict[key] = value

                else:
                    raise NotImplementedError

                i += len(step.values)

            yield index, parameter_dict

    def _sequential_parameters(self) -> Iterator[tuple[int, dict]]:
        """Generate sequential mode parameters.

        Yields
        ------
        index: int
        parameter_dict: dict
        """
        step: ParameterValues
        for step in self.enabled_steps:
            key: str = step.key
            for index, value in enumerate(step):
                parameter_dict = {key: value}
                yield index, parameter_dict

    def _product_indices(self) -> "Iterator[Tuple]":
        """Return an iterator of product parameter indices.

        Returns
        -------
        iterator
        """
        step_ranges = [range(len(step)) for step in self.enabled_steps]
        out = itertools.product(*step_ranges)
        return out

    def _product_parameters(
        self,
    ) -> Iterator[tuple[tuple, dict[str, Any]]]:
        """Generate product mode parameters.

        Yields
        ------
        indices: tuple
        parameter_dict: dict
        """
        all_steps = self.enabled_steps
        keys = [step.key for step in self.enabled_steps]
        for indices, params in zip(
            self._product_indices(), itertools.product(*all_steps)
        ):
            parameter_dict = {}
            for key, value in zip(keys, params):
                parameter_dict.update({key: value})
            yield indices, parameter_dict

    # TODO: This function will be deprecated (see #563)
    def _parameter_it(self) -> Iterator[tuple]:
        """Return the method for generating parameters based on parametric mode."""
        if self.parameter_mode == ParameterMode.Product:
            yield from self._product_parameters()

        elif self.parameter_mode == ParameterMode.Sequential:
            yield from self._sequential_parameters()

        elif self.parameter_mode == ParameterMode.Custom:
            yield from self._custom_parameters()
        else:
            raise NotImplementedError

    def _get_parameters_item(
        self, processor: "Processor"
    ) -> Sequence[Union[ParameterItem, CustomParameterItem]]:
        if self.parameter_mode == ParameterMode.Product:
            params_it: Iterator = self._product_parameters()

            return [
                ParameterItem(index=index, parameters=parameter_dict, run_index=n)
                for n, (index, parameter_dict) in enumerate(params_it)
            ]

        elif self.parameter_mode == ParameterMode.Sequential:
            # Get default values for all unique parameters
            params_all_keys: Sequence[str] = [
                param_value.key for param_value in self.enabled_steps
            ]
            params_unique_keys: Iterator[str] = toolz.unique(params_all_keys)

            params_defaults: Mapping[str, np.ndarray] = {
                key: processor.get(key) for key in params_unique_keys
            }

            params_it = self._sequential_parameters()

            return [
                CustomParameterItem(
                    index=index,
                    parameters=params_defaults | parameter_dict,
                    run_index=n,
                )
                for n, (index, parameter_dict) in enumerate(params_it)
            ]

        elif self.parameter_mode == ParameterMode.Custom:
            params_it = self._custom_parameters()

            return [
                CustomParameterItem(index=index, parameters=parameter_dict, run_index=n)
                for n, (index, parameter_dict) in enumerate(params_it)
            ]

        else:
            raise ValueError("Parametric mode not specified.")

    def _processors_it(
        self, processor: "Processor"
    ) -> Iterator[tuple["Processor", Union[int, tuple[int]], dict]]:
        """Generate processors with different product parameters.

        Parameters
        ----------
        processor: Processor

        Yields
        ------
        new_processor: Processor
        index: tuple of int
        parameter_dict: dict
        """

        for index, parameter_dict in self._parameter_it():
            new_processor = create_new_processor(
                processor=processor,
                parameter_dict=parameter_dict,
            )
            yield new_processor, index, parameter_dict

    def _get_parameter_types(self) -> Mapping[str, ParameterType]:
        """Check for each step if parameters can be used as dataset coordinates (1D, simple) or not (multi)."""
        for step in self.enabled_steps:
            self.parameter_types.update({step.key: step.type})
        return self.parameter_types

    def run_debug_mode(
        self, processor: "Processor"
    ) -> tuple[list["Processor"], "xr.Dataset"]:
        """Run observation pipelines in debug mode and return list of processors and parameter logs.

        Parameters
        ----------
        processor: Processor

        Returns
        -------
        processors: list
        final_logs: Dataset
        """
        # Late import to speedup start-up time
        import xarray as xr

        processors = []
        logs: list[xr.Dataset] = []

        for processor_id, (proc, _index, parameter_dict) in enumerate(
            tqdm(self._processors_it(processor))
        ):
            log: xr.Dataset = log_parameters(
                processor_id=processor_id, parameter_dict=parameter_dict
            )
            logs.append(log)
            _ = run_exposure_pipeline(
                processor=proc,
                readout=self.readout,
                outputs=self.outputs,
                pipeline_seed=self.pipeline_seed,
            )
            processors.append(processor)

        # See issue #276
        final_logs = xr.combine_by_coords(logs)
        if not isinstance(final_logs, xr.Dataset):
            raise TypeError("Expecting 'Dataset'.")

        return processors, final_logs

    def validate_steps(self, processor: "Processor") -> None:
        """Validate enabled parameter steps in processor before running the pipelines.

        Parameters
        ----------
        processor: Processor

        Raises
        ------
        KeyError
            If a 'step' is missing in the configuration.
        ValueError
            If a model referenced in the configuration has not been enabled.
        """
        step: ParameterValues
        for step in self.enabled_steps:
            key: str = step.key
            if not processor.has(key):
                raise KeyError(f"Missing parameter: {key!r} in steps.")

            # TODO: the string literal expressions are difficult to maintain.
            #     Example: 'pipeline.', '.arguments', '.enabled'
            #     We may want to consider an API for this.
            # Proposed API:
            # value = operator.attrgetter(step.key)(processor)
            if "pipeline." in key:
                model_name: str = key[: key.find(".arguments")]
                model_enabled: str = model_name + ".enabled"
                if not processor.get(model_enabled):
                    raise ValueError(
                        f"The '{model_name}' model referenced in Observation configuration "
                        f"has not been enabled in yaml config!"
                    )

            if (
                any(x == "_" for x in step.values[:])
                and self.parameter_mode != ParameterMode.Custom
            ):
                raise ValueError(
                    "Either define 'custom' as parametric mode or "
                    "do not use '_' character in 'values' field"
                )

    # TODO: This method will be deprecated (see #563)
    def run_observation(self, processor: "Processor") -> ObservationResult:
        """Run the observation pipelines.

        Parameters
        ----------
        processor : Processor

        Returns
        -------
        Result
        """
        # Late import to speedup start-up time
        import xarray as xr

        # validation
        self.validate_steps(processor)

        types: Mapping[str, ParameterType] = self._get_parameter_types()

        dim_names: Mapping[str, str] = _get_short_dimension_names(types)

        y = range(processor.detector.geometry.row)
        x = range(processor.detector.geometry.col)
        times = self.readout.times

        if self.parameter_mode == ParameterMode.Product:
            apply_pipeline = partial(
                self._apply_exposure_pipeline_product,
                dimension_names=dim_names,
                x=x,
                y=y,
                processor=processor,
                times=times,
                types=types,
            )
            lst = [
                (index, parameter_dict, n)
                for n, (index, parameter_dict) in enumerate(self._parameter_it())
            ]

            if self.with_dask:
                dataset_list = db.from_sequence(lst).map(apply_pipeline).compute()
            else:
                dataset_list = list(map(apply_pipeline, tqdm(lst)))

            # prepare lists for to-be-merged datasets
            parameters: list[list[xr.Dataset]] = [
                [] for _ in range(len(self.enabled_steps))
            ]
            logs = []

            for processor_id, (indices, parameter_dict, _) in enumerate(lst):
                # log parameters for this pipeline
                log = log_parameters(
                    processor_id=processor_id, parameter_dict=parameter_dict
                )
                logs.append(log)

                # save parameters with appropriate product mode indices
                for i, coordinate in enumerate(parameter_dict):
                    parameter_ds = parameter_to_dataset(
                        parameter_dict=parameter_dict,
                        dimension_names=dim_names,
                        index=indices[i],
                        coordinate_name=coordinate,
                    )
                    parameters[i].append(parameter_ds)

            # merging/combining the outputs
            final_parameters_list: list[xr.Dataset] = []
            for p in parameters:
                # See issue #276
                new_dataset = xr.combine_by_coords(p)
                if not isinstance(new_dataset, xr.Dataset):
                    raise TypeError("Expecting 'Dataset'.")

                final_parameters_list.append(new_dataset)

            final_parameters_merged = xr.merge(final_parameters_list)

            # See issue #276
            final_logs = xr.combine_by_coords(logs)
            if not isinstance(final_logs, xr.Dataset):
                raise TypeError("Expecting 'Dataset'.")

            # See issue #276
            final_dataset = xr.combine_by_coords(dataset_list)
            if not isinstance(final_dataset, xr.Dataset):
                raise TypeError("Expecting 'Dataset'.")

            result = ObservationResult(
                dataset=final_dataset,
                parameters=final_parameters_merged,
                logs=final_logs,
            )

            return result

        elif self.parameter_mode == ParameterMode.Sequential:
            apply_pipeline = partial(
                self._apply_exposure_pipeline_sequential,
                dimension_names=dim_names,
                x=x,
                y=y,
                processor=processor,
                times=times,
                types=types,
            )

            lst = [
                (index, parameter_dict, n)
                for n, (index, parameter_dict) in enumerate(self._parameter_it())
            ]

            if self.with_dask:
                dataset_list = db.from_sequence(lst).map(apply_pipeline).compute()
            else:
                dataset_list = list(map(apply_pipeline, tqdm(lst)))

            # prepare lists/dictionaries for to-be-merged datasets
            parameters = [[] for _ in range(len(self.enabled_steps))]
            logs = []

            # overflow to next parameter step counter
            step_counter = -1

            for processor_id, (index, parameter_dict, _) in enumerate(lst):
                # log parameters for this pipeline
                # TODO: somehow refactor logger so that default parameters
                #  from other steps are also logged in sequential mode
                log = log_parameters(
                    processor_id=processor_id, parameter_dict=parameter_dict
                )
                logs.append(log)

                # Figure out current coordinate
                coordinate = str(list(parameter_dict)[0])
                # Check for overflow to next parameter
                if index == 0:
                    step_counter += 1

                # save sequential parameter with appropriate index
                parameter_ds = parameter_to_dataset(
                    parameter_dict=parameter_dict,
                    dimension_names=dim_names,
                    index=index,
                    coordinate_name=coordinate,
                )
                parameters[step_counter].append(parameter_ds)

            # merging/combining the outputs
            # See issue #276
            final_logs = xr.combine_by_coords(logs)
            if not isinstance(final_logs, xr.Dataset):
                raise TypeError("Expecting 'Dataset'.")

            final_datasets = compute_final_sequential_dataset(
                list_of_index_and_parameter=lst,
                list_of_datasets=dataset_list,
                dimension_names=dim_names,
            )

            final_parameters_list = []
            for p in parameters:
                # See issue #276
                new_dataset = xr.combine_by_coords(p)
                if not isinstance(new_dataset, xr.Dataset):
                    raise TypeError("Expecting 'Dataset'.")

                final_parameters_list.append(new_dataset)

            final_parameters_merged = xr.merge(final_parameters_list)

            result = ObservationResult(
                dataset=final_datasets,
                parameters=final_parameters_merged,
                logs=final_logs,
            )
            return result

        elif self.parameter_mode == ParameterMode.Custom:
            apply_pipeline = partial(
                self._apply_exposure_pipeline_custom,
                x=x,
                y=y,
                processor=processor,
                times=times,
            )
            lst = [
                (index, parameter_dict, n)
                for n, (index, parameter_dict) in enumerate(self._parameter_it())
            ]

            if self.with_dask:
                dataset_list = db.from_sequence(lst).map(apply_pipeline).compute()
            else:
                dataset_list = list(map(apply_pipeline, tqdm(lst)))

            # prepare lists for to-be-merged datasets
            logs = []

            for index, parameter_dict, _ in lst:
                # log parameters for this pipeline
                log = log_parameters(processor_id=index, parameter_dict=parameter_dict)
                logs.append(log)

            # merging/combining the outputs
            final_ds = xr.combine_by_coords(dataset_list)
            final_log = xr.combine_by_coords(logs)

            # See issue #276
            if not isinstance(final_ds, xr.Dataset):
                raise TypeError("Expecting 'Dataset'.")
            if not isinstance(final_log, xr.Dataset):
                raise TypeError("Expecting 'Dataset'.")

            final_parameters = final_log  # parameter dataset same as logs

            result = ObservationResult(
                dataset=final_ds, parameters=final_parameters, logs=final_log
            )
            return result

        else:
            raise ValueError("Parametric mode not specified.")

    def run_observation_datatree(self, processor: "Processor") -> "DataTree":
        """Run the observation pipelines."""
        # Late import to speedup start-up time
        from datatree import DataTree

        # validation
        self.validate_steps(processor)

        types: Mapping[str, ParameterType] = self._get_parameter_types()
        dim_names: Mapping[str, str] = _get_short_dimension_names_new(types)

        apply_pipeline: Callable[
            [Union[ParameterItem, CustomParameterItem]], DataTree
        ] = partial(
            self._apply_exposure_pipeline_new,
            dimension_names=dim_names,
            processor=processor,
            types=types,
        )

        parameters: Sequence[
            Union[ParameterItem, CustomParameterItem]
        ] = self._get_parameters_item(processor=processor)

        if self.with_dask:
            datatree_bag: db.Bag = (
                db.from_sequence(parameters)
                .map(apply_pipeline)
                .fold(binop=DataTree.combine_first, combine=DataTree.combine_first)  # type: ignore
            )
            final_datatree: DataTree = datatree_bag.compute()
        else:
            datatree_list: Iterator[DataTree] = (
                apply_pipeline(el) for el in tqdm(parameters)
            )
            final_datatree = reduce(DataTree.combine_first, datatree_list)  # type: ignore

        parameter_name: str = self.parameter_mode.name
        final_datatree.attrs["running mode"] = f"Observation - {parameter_name}"

        # See issue #276. TODO: Is this still valid ?
        # if not isinstance(final_dataset, xr.Dataset):
        #     raise TypeError("Expecting 'Dataset'.")

        return final_datatree

    # TODO: This function will be deprecated (see #563)
    def _apply_exposure_pipeline_product(
        self,
        index_and_parameter: tuple[
            tuple[int, ...],
            Mapping[
                str,
                Union[str, Number, np.ndarray, list[Union[str, Number, np.ndarray]]],
            ],
            int,
        ],
        dimension_names: Mapping[str, str],
        processor: "Processor",
        x: range,
        y: range,
        times: np.ndarray,
        types: Mapping[str, ParameterType],
    ) -> "xr.Dataset":
        index, parameter_dict, n = index_and_parameter

        new_processor = create_new_processor(
            processor=processor, parameter_dict=parameter_dict
        )

        # run the pipeline
        _ = run_exposure_pipeline(
            processor=new_processor,
            readout=self.readout,
            result_type=self.result_type,
            pipeline_seed=self.pipeline_seed,
        )

        _ = self.outputs.save_to_file(processor=new_processor, run_number=n)

        ds: xr.Dataset = new_processor.result_to_dataset(
            x=x,
            y=y,
            times=times,
            result_type=self.result_type,
        )

        # Can also be done outside dask in a loop
        ds = _add_product_parameters(
            ds=ds,
            parameter_dict=parameter_dict,
            dimension_names=dimension_names,
            indices=index,
            types=types,
        )

        ds.attrs.update({"running mode": "Observation - Product"})

        return ds

    def _apply_exposure_pipeline_new(
        self,
        param_item: Union[ParameterItem, CustomParameterItem],
        dimension_names: Mapping[str, str],
        processor: "Processor",
        types: Mapping[str, ParameterType],
    ) -> "DataTree":
        new_processor = create_new_processor(
            processor=processor,
            parameter_dict=param_item.parameters,
        )

        # run the pipeline
        data_tree: "DataTree" = run_pipeline(
            processor=new_processor,
            readout=self.readout,
            result_type=self.result_type,
            pipeline_seed=self.pipeline_seed,
        )

        _ = self.outputs.save_to_file(
            processor=new_processor,
            run_number=param_item.run_index,
        )

        # Can also be done outside dask in a loop
        if isinstance(param_item, ParameterItem):
            final_data_tree = _add_product_parameters_datatree(
                data_tree=data_tree,
                parameter_dict=param_item.parameters,
                indexes=param_item.index,
                dimension_names=dimension_names,
                types=types,
            )

        else:
            final_data_tree = _add_custom_parameters_datatree(
                data_tree=data_tree,
                parameter_dict=param_item.parameters,
                index=param_item.index,
                dimension_names=dimension_names,
                types=types,
            )

        return final_data_tree

    # TODO: This function will be deprecated (see #563)
    def _apply_exposure_pipeline_custom(
        self,
        index_and_parameter: tuple[
            int,
            Mapping[
                str,
                Union[str, Number, np.ndarray, list[Union[str, Number, np.ndarray]]],
            ],
            int,
        ],
        processor: "Processor",
        x: range,
        y: range,
        times: np.ndarray,
    ):
        index, parameter_dict, n = index_and_parameter

        new_processor = create_new_processor(
            processor=processor,
            parameter_dict=parameter_dict,
        )

        # run the pipeline
        _ = run_exposure_pipeline(
            processor=new_processor,
            readout=self.readout,
            result_type=self.result_type,
            pipeline_seed=self.pipeline_seed,
        )

        _ = self.outputs.save_to_file(processor=new_processor, run_number=n)

        ds: xr.Dataset = new_processor.result_to_dataset(
            x=x, y=y, times=times, result_type=self.result_type
        )

        # Can also be done outside dask in a loop
        ds = _add_custom_parameters(
            ds=ds,
            index=index,
        )
        ds.attrs.update({"running mode": "Observation - Custom"})

        return ds

    # TODO: This function will be deprecated (see #563)
    def _apply_exposure_pipeline_sequential(
        self,
        index_and_parameter: tuple[
            int,
            Mapping[
                str,
                Union[str, Number, np.ndarray, list[Union[str, Number, np.ndarray]]],
            ],
            int,
        ],
        dimension_names: Mapping[str, str],
        processor: "Processor",
        x: range,
        y: range,
        times: np.ndarray,
        types: Mapping[str, ParameterType],
    ):
        index, parameter_dict, n = index_and_parameter

        new_processor = create_new_processor(
            processor=processor,
            parameter_dict=parameter_dict,
        )

        coordinate = str(list(parameter_dict)[0])

        # run the pipeline
        _ = run_exposure_pipeline(
            processor=new_processor,
            readout=self.readout,
            result_type=self.result_type,
            pipeline_seed=self.pipeline_seed,
        )

        _ = self.outputs.save_to_file(processor=new_processor, run_number=n)

        ds: xr.Dataset = new_processor.result_to_dataset(
            x=x, y=y, times=times, result_type=self.result_type
        )

        # Can also be done outside dask in a loop
        ds = _add_sequential_parameters(
            ds=ds,
            parameter_dict=parameter_dict,
            dimension_names=dimension_names,
            index=index,
            coordinate_name=coordinate,
            types=types,
        )

        ds.attrs.update({"running mode": "Observation - Sequential"})

        return ds

    def debug_parameters(self, processor: "Processor") -> list:
        """List the parameters using processor parameters in processor generator.

        Parameters
        ----------
        processor: Processor

        Returns
        -------
        result: list
        """
        result = []
        processor_generator = self._processors_it(processor=processor)
        for i, (proc, _, _) in enumerate(processor_generator):
            values = []
            for step in self.enabled_steps:
                _, att = get_obj_att(proc, step.key)
                value = get_value(proc, step.key)
                values.append((att, value))
            logging.debug("%d: %r" % (i, values))
            result.append((i, values))
        return result


def create_new_processor(
    processor: "Processor",
    parameter_dict: Mapping[
        str, Union[str, Number, np.ndarray, list[Union[str, Number, np.ndarray]]]
    ],
) -> "Processor":
    """Create a copy of processor and set new attributes from a dictionary before returning it.

    Parameters
    ----------
    processor: Processor
    parameter_dict: dict

    Returns
    -------
    Processor
    """

    new_processor = deepcopy(processor)

    for key in parameter_dict.keys():
        new_processor.set(key=key, value=parameter_dict[key])

    return new_processor


def _id(s: str) -> str:
    """Add _id to the end of a string."""
    out = s + "_id"
    return out


def short(s: str) -> str:
    """Split string with . and return the last element."""
    out = s.split(".")[-1]
    return out


def log_parameters(processor_id: int, parameter_dict: dict) -> "xr.Dataset":
    """Return parameters in the current processor in a xarray dataset.

    Parameters
    ----------
    processor_id: int
    parameter_dict: dict

    Returns
    -------
    Dataset
    """
    # Late import to speedup start-up time
    import xarray as xr

    out = xr.Dataset()
    for key, value in parameter_dict.items():
        da = xr.DataArray(value)
        da = da.assign_coords(coords={"id": processor_id})
        da = da.expand_dims(dim="id")
        out[short(key)] = da
    return out


def parameter_to_dataset(
    parameter_dict: dict,
    dimension_names: Mapping[str, str],
    index: int,
    coordinate_name: str,
) -> "xr.Dataset":
    """Return a specific parameter dataset from a parameter dictionary.

    Parameters
    ----------
    parameter_dict: dict
    dimension_names
    index: int
    coordinate_name: str

    Returns
    -------
    Dataset
    """
    # Late import to speedup start-up time
    import xarray as xr

    parameter_ds = xr.Dataset()
    parameter = xr.DataArray(parameter_dict[coordinate_name])

    # TODO: Dirty hack. Fix this !
    short_name: str = dimension_names[coordinate_name]

    if short_name.endswith("_id"):
        short_coord_name = short_name[:-3]
        short_coord_name_id = short_name
    else:
        short_coord_name = short_name
        short_coord_name_id = f"{short_name}_id"

    parameter = parameter.assign_coords({short_coord_name_id: index})
    parameter = parameter.expand_dims(dim=short_coord_name_id)
    parameter_ds[short_coord_name] = parameter

    return parameter_ds


# TODO: This function will be deprecated (see #563)
def _add_custom_parameters(ds: "xr.Dataset", index: int) -> "xr.Dataset":
    """Add coordinate "index" to the dataset.

    Parameters
    ----------
    ds: Dataset
    index: int

    Returns
    -------
    Dataset
    """

    ds = ds.assign_coords({"id": index})
    ds = ds.expand_dims(dim="id")

    return ds


def _add_custom_parameters_datatree(
    data_tree: "DataTree",
    parameter_dict: Mapping[str, Union[str, Number, ArrayLike]],
    index: int,
    dimension_names: Mapping[str, str],
    types: Mapping[str, ParameterType],
) -> "DataTree":
    """Add coordinate "index" to the dataset.

    Parameters
    ----------
    data_tree: Dataset
    index: int

    Returns
    -------
    DataTree
    """
    import pandas as pd
    import xarray as xr

    data_tree = data_tree.expand_dims({"id": [index]})

    for coordinate_name, param_value in parameter_dict.items():
        short_name: str = dimension_names[coordinate_name]

        #  assigning the right coordinates based on type
        if types[coordinate_name] == ParameterType.Simple:
            data_tree = data_tree.assign_coords(
                {short_name: ("id", pd.Index([param_value]))}
            )

        elif types[coordinate_name] == ParameterType.Multi:
            data = np.array(param_value)
            data_array = xr.DataArray(data).expand_dims({"id": [index]})
            data_tree = data_tree.assign_coords({short_name: data_array})

        else:
            raise NotImplementedError

    return data_tree


# TODO: This function will be deprecated (see #563)
def _add_sequential_parameters(
    ds: "xr.Dataset",
    parameter_dict: Mapping[
        str, Union[str, Number, np.ndarray, list[Union[str, Number, np.ndarray]]]
    ],
    dimension_names: Mapping[str, str],
    index: int,
    coordinate_name: str,
    types: Mapping[str, ParameterType],
) -> "xr.Dataset":
    """Add true coordinates or index to sequential mode dataset.

    Parameters
    ----------
    ds : Dataset
    parameter_dict : dict
    dimension_names
    index : int
    coordinate_name : str
    types : dict

    Returns
    -------
    Dataset
    """

    #  assigning the right coordinates based on type
    short_name: str = dimension_names[coordinate_name]

    if types[coordinate_name] == ParameterType.Simple:
        ds = ds.assign_coords(coords={short_name: parameter_dict[coordinate_name]})
        ds = ds.expand_dims(dim=short_name)

    elif types[coordinate_name] == ParameterType.Multi:
        ds = ds.assign_coords({short_name: index})
        ds = ds.expand_dims(dim=short_name)

    return ds


# TODO: This function will be deprecated (see #563)
def _add_product_parameters(
    ds: "xr.Dataset",
    parameter_dict: Mapping[
        str, Union[str, Number, np.ndarray, list[Union[str, Number, np.ndarray]]]
    ],
    dimension_names: Mapping[str, str],
    indices: tuple[int, ...],
    types: Mapping[str, ParameterType],
) -> "xr.Dataset":
    """Add true coordinates or index to product mode dataset.

    Parameters
    ----------
    ds: Dataset
    parameter_dict: dict
    indices: tuple
    types: dict

    Returns
    -------
    Dataset
    """
    # TODO: Implement for coordinate 'multi'
    for i, (coordinate_name, param_value) in enumerate(parameter_dict.items()):
        short_name: str = dimension_names[coordinate_name]

        #  assigning the right coordinates based on type
        if types[coordinate_name] == ParameterType.Simple:
            ds = ds.assign_coords(coords={short_name: param_value})
            ds = ds.expand_dims(dim=short_name)

        elif types[coordinate_name] == ParameterType.Multi:
            ds = ds.assign_coords({short_name: indices[i]})
            ds = ds.expand_dims(dim=short_name)

        else:
            raise NotImplementedError

    return ds


def to_tuples(data: Iterable) -> tuple:
    lst: list = []
    for el in data:
        if isinstance(el, Iterable) and not isinstance(el, str):
            lst.append(to_tuples(el))
        else:
            lst.append(el)

    return tuple(lst)


def _add_product_parameters_datatree(
    data_tree: "DataTree",
    parameter_dict: Mapping[str, Union[str, Number, ArrayLike]],
    indexes: tuple[int, ...],
    dimension_names: Mapping[str, str],
    types: Mapping[str, ParameterType],
) -> "DataTree":
    """Add true coordinates or index to product mode dataset.

    Parameters
    ----------
    data_tree : DataTree
    parameter_dict : dict
    types : dict

    Returns
    -------
    DataTree
    """
    import xarray as xr

    # TODO: join 'indexes' and 'parameter_dict'
    for index, (coordinate_name, param_value) in zip(indexes, parameter_dict.items()):
        short_name: str = dimension_names[coordinate_name]

        #  assigning the right coordinates based on type
        if types[coordinate_name] == ParameterType.Simple:
            data_tree = data_tree.expand_dims(dim={short_name: [param_value]})

        elif types[coordinate_name] == ParameterType.Multi:
            data = np.array(param_value)
            data_array = xr.DataArray(data).expand_dims(
                dim={f"{short_name}_id": [index]}
            )
            data_tree = data_tree.expand_dims(
                {f"{short_name}_id": [index]}
            ).assign_coords({short_name: data_array})

        else:
            raise NotImplementedError

    return data_tree


def compute_final_sequential_dataset(
    list_of_index_and_parameter: list,
    list_of_datasets: list,
    dimension_names: Mapping[str, str],
) -> dict[str, "xr.Dataset"]:
    """Return a dictionary of result datasets where keys are different parameters.

    Parameters
    ----------
    list_of_index_and_parameter: list
    list_of_datasets: list
    dimension_names

    Returns
    -------
    dict
    """
    # Late import to speedup start-up time
    import xarray as xr

    final_dict: dict[str, list[xr.Dataset]] = {}

    for _, parameter_dict, n in list_of_index_and_parameter:
        coordinate = str(list(parameter_dict)[0])
        coordinate_short: str = dimension_names[coordinate]

        if short(coordinate) not in final_dict:
            final_dict.update({coordinate_short: []})
            final_dict[coordinate_short].append(list_of_datasets[n])
        else:
            final_dict[coordinate_short].append(list_of_datasets[n])

    final_datasets: dict[str, xr.Dataset] = {}
    for key, value in final_dict.items():
        ds = xr.combine_by_coords(value)
        # see issue #276
        if not isinstance(ds, xr.Dataset):
            raise TypeError("Expecting 'Dataset'.")

        final_datasets.update({key: ds})

    return final_datasets
