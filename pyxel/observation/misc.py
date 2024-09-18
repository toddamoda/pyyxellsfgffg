#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Subpackage for managing and manipulating parameter sets for product, sequential and custom modes."""

import itertools
from collections import Counter
from collections.abc import Iterator, Mapping, MutableMapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from itertools import chain, count
from numbers import Number
from typing import TYPE_CHECKING, Any, Optional, Union

import numpy as np
from typing_extensions import Literal, Self

from pyxel.observation import ParameterValues

if TYPE_CHECKING:
    import pandas as pd
    import xarray as xr

    from pyxel.pipelines import Processor

ParametersType = MutableMapping[
    str,
    Union[
        str,
        Number,
        np.ndarray,
        Sequence[Union[str, Number, np.ndarray]],
    ],
]


@dataclass(frozen=True)
class ParameterEntry:
    """Internal Parameter Item."""

    # TODO: Merge 'index' and 'parameters'
    index: tuple[int, ...]
    parameters: ParametersType
    run_index: int


@dataclass(frozen=True)
class CustomParameterEntry:
    """Internal Parameter Item."""

    # TODO: Merge 'index' and 'parameters'
    index: int
    parameters: ParametersType
    run_index: int


@dataclass
class ProductMode:
    """Class for managing product combinations of parameter values.

    Attributes
    ----------
    parameters : Sequence[ParameterValues]
        A sequence of ParameterValues that defines the possible parameter sets.
    """

    parameters: Sequence[ParameterValues]

    @property
    def enabled_steps(self) -> Sequence[ParameterValues]:
        """Return a list of enabled ParameterValues."""
        out = [step for step in self.parameters if step.enabled]
        return out

    def _product_indices(self) -> Iterator[tuple]:
        """Generate all possible index combinations for the enabled parameters.

        Returns
        -------
        Iterator[tuple]
            An iterator over the product of indices of enabled parameter values.
        """
        step_ranges = [range(len(step)) for step in self.enabled_steps]
        out = itertools.product(*step_ranges)
        return out

    def _product_parameters(self) -> Iterator[tuple[tuple, dict[str, Any]]]:
        """Generate all combinations of parameter values."""
        all_steps = self.enabled_steps
        keys = [step.key for step in self.enabled_steps]
        for indices, params in zip(
            self._product_indices(), itertools.product(*all_steps)
        ):
            parameter_dict = {}
            for key, value in zip(keys, params):
                parameter_dict.update({key: value})
            yield indices, parameter_dict

    def get_parameters_item(
        self,
    ) -> Sequence[Union[ParameterEntry, CustomParameterEntry]]:
        params_it: Iterator = self._product_parameters()

        return [
            ParameterEntry(index=index, parameters=parameter_dict, run_index=n)
            for n, (index, parameter_dict) in enumerate(params_it)
        ]

    # TODO: Add unit tests
    def create_params(self, dim_names: Mapping[str, str]) -> "xr.DataArray":
        """Create an xarray DataArray based on the combinations of enabled parameter values.

        Parameters
        ----------
        dim_names : Mapping[str, str]
            A mapping of parameter keys to their corresponding dimension names for xarray.

        Returns
        -------
        xr.DataArray
            An xarray DataArray representing the parameter combinations.
        """
        # Late import to speedup start-up time
        import pandas as pd

        all_steps: Mapping[str, Sequence[Any]] = {
            step.key: list(step) for step in self.enabled_steps
        }
        params_names = [dim_names[key] for key in all_steps]
        params_indexes = pd.MultiIndex.from_product(
            list(all_steps.values()), names=params_names
        )

        # Create a Pandas MultiIndex
        params_serie = pd.Series(list(params_indexes), index=params_indexes)
        params_dataarray: "xr.DataArray" = params_serie.to_xarray()

        return params_dataarray


@dataclass
class SequentialMode:
    """Class for managing sequential execution of parameter sets.

    Attributes
    ----------
    parameters : Sequence[ParameterValues]
        A sequence of ParameterValues that defines the possible parameter sets.
    """

    parameters: Sequence[ParameterValues]

    @property
    def enabled_steps(self) -> Sequence[ParameterValues]:
        """Return a list of enabled ParameterValues."""
        out = [step for step in self.parameters if step.enabled]
        return out

    def _sequential_parameters(self) -> Iterator[tuple[int, ParametersType]]:
        """Generate sequential mode parameters."""
        index = 0

        step: ParameterValues
        for step in self.enabled_steps:
            key: str = step.key
            for value in step:
                parameter_dict: ParametersType = {key: value}
                yield index, parameter_dict

                index += 1

    def get_parameters_item(
        self, processor: "Processor"
    ) -> Sequence[Union[ParameterEntry, CustomParameterEntry]]:
        # Late import to speedup start-up time
        import toolz

        # Get default values for all unique parameters
        params_all_keys: Sequence[str] = [
            param_value.key for param_value in self.enabled_steps
        ]
        params_unique_keys: Iterator[str] = toolz.unique(params_all_keys)

        params_defaults: ParametersType = {
            key: processor.get(key) for key in params_unique_keys
        }

        params_it = self._sequential_parameters()

        return [
            CustomParameterEntry(
                index=index,
                parameters={**params_defaults, **parameter_dict},
                run_index=n,
            )
            for n, (index, parameter_dict) in enumerate(params_it)
        ]

    # TODO: Add unit tests
    def create_params(self, dim_names: Mapping[str, str]) -> "xr.DataArray":
        """Create an xarray DataArray representing the sequence of parameter steps.

        Parameters
        ----------
        dim_names : Mapping[str, str]
            A mapping of parameter keys to their corresponding dimension names for xarray.

        Returns
        -------
        xr.DataArray
            An xarray DataArray representing the sequential steps.
        """
        # Late import to speedup start-up time
        import pandas as pd

        all_steps: Mapping[str, Sequence[Any]] = {
            step.key: list(step) for step in self.enabled_steps
        }
        params_names = [dim_names[key] for key in all_steps]

        params_sequential_list = list(zip(*all_steps.values()))
        params_sequential_with_index = [
            (idx, *el) for idx, el in zip(count(), params_sequential_list)
        ]

        params_sequential_dataframe = pd.DataFrame(
            params_sequential_with_index,
            columns=["id", *params_names],
        )
        params_sequential_dataframe["custom_values"] = params_sequential_list

        params_sequential_data_array: "xr.DataArray" = (
            params_sequential_dataframe.set_index("id")
            .to_xarray()
            .set_coords([dim_names[key] for key in all_steps])["custom_values"]
        )

        return params_sequential_data_array


# TODO: Move this to 'ModeCustom' ?
def convert_custom_data(
    custom_data: "pd.DataFrame",
    params_custom_list: Sequence,
    params_names: Sequence[str],
) -> "pd.DataFrame":
    """Transform data for custom mode into a formatted DataFrame.

    Parameters
    ----------
    custom_data : DataFrame
        Input data containing columns to be mapped to parameters. Each column represents a
        potential parameter or part of a parameter group.
    params_custom_list
    params_names : Sequence
        A list of strings that represent the names of the parameters to be assigned to the
        columns of the resulting DataFrame. Each name corresponds to an entry in `params_custom_list`.

    Examples
    --------
    >>> custom_data = pd.DataFrame(
    ...     {
    ...         0: {0: 0.3, 1: 0.3},
    ...         1: {0: 3, 1: 5},
    ...         2: {0: 5, 1: 7},
    ...     }
    ... )
    >>> custom_data
         0  1  2
    0  0.3  3  5
    1  0.3  5  7

    >>> params_custom_list = [["_"], ["_", "_"]]
    >>> params_names = ["beta", "trap_densities"]

    >>> convert_custom_data(
    ...     custom_data=custom_data,
    ...     params_custom_list=params_custom_list,
    ...     params_names=params_names,
    ... )
       beta trap_densities
    0   0.3         (3, 5)
    1   0.3         (5, 7)

    Returns
    -------
    DataFrame

    Notes
    -----
    - The length of `params_custom_list` should match the length of `params_names`.
    - If an entry in `params_custom_list` contains multiple placeholders (e.g., `["_", "_"]`),
      the corresponding columns in `custom_data` will be combined into tuples in the resulting DataFrame.
    """

    # Late import to speedup start-up time
    import pandas as pd

    new_custom_data = pd.DataFrame()
    num_columns = len(custom_data.columns)

    idx = 0
    params: Sequence[Literal["_"]]
    for name, params in zip(params_names, params_custom_list):
        if len(params) == 1:
            assert idx < num_columns
            new_custom_data[name] = custom_data[idx]
            idx += 1

        else:
            assert (idx + len(params)) <= num_columns
            columns = [cnt for cnt, _ in zip(count(idx), params)]
            new_values: list[list] = custom_data[columns].values.tolist()
            new_values_tuples: Sequence[tuple] = [tuple(el) for el in new_values]

            new_custom_data[name] = new_values_tuples

            idx += len(params)

    return new_custom_data


@dataclass
class CustomMode:
    """Class for managing custom parameter sets from an external file.

    Attributes
    ----------
    parameters : Sequence[ParameterValues]
        A sequence of ParameterValues.
    custom_data : pd.DataFrame
        The custom parameter data loaded from a file.
    """

    parameters: Sequence[ParameterValues]
    custom_data: "pd.DataFrame"

    @property
    def enabled_steps(self) -> Sequence[ParameterValues]:
        """Return a list of enabled ParameterValues."""
        out = [step for step in self.parameters if step.enabled]
        return out

    @classmethod
    def build(
        cls,
        parameters: Sequence[ParameterValues],
        custom_file: str,
        custom_columns: Optional[slice],
    ) -> Self:
        """Load custom parameters from a file and validate.

        Parameters
        ----------
        parameters : Sequence[ParameterValues]
            The parameter definitions.
        custom_file : str
            Path to the custom parameter data file.
        custom_columns : Optional[slice]
            Slice specifying the columns to use from the custom file.

        Returns
        -------
        CustomMode
            An instance of ModeCustom with the custom data loaded.
        """
        from pyxel import load_table

        # Read the file without forcing its data type
        all_data: "pd.DataFrame" = load_table(custom_file, dtype=None)
        filtered_data: "pd.DataFrame" = all_data.loc[:, custom_columns]

        # Sanity check
        num_columns = len(filtered_data.columns)
        enabled_steps: Sequence[ParameterValues] = [
            step for step in parameters if step.enabled
        ]

        all_values = [list(el.values) for el in enabled_steps]

        counter = Counter(chain.from_iterable(all_values))
        if "_" not in counter:
            raise ValueError("Missing at parameter '_'")

        num_parameters: int = counter["_"]
        if num_parameters != num_columns:
            raise ValueError(
                f"Custom data file has {num_columns} column(s). "
                f"{num_parameters} is/are expected ! "
            )

        return cls(parameters=parameters, custom_data=filtered_data)

    # TODO: Add unit tests
    def create_params(self, dim_names: Mapping[str, str]) -> "xr.DataArray":
        """Create an xarray DataArray representing the custom parameter data.

        Parameters
        ----------
        dim_names : Mapping[str, str]
            A mapping of parameter keys to their corresponding dimension names for xarray.

        Returns
        -------
        xr.DataArray
            An xarray DataArray representing the custom parameters.
        """
        all_steps: Mapping[str, Sequence[Any]] = {
            step.key: list(step) for step in self.enabled_steps
        }
        params_names = [dim_names[key] for key in all_steps]

        params_custom_list = list(all_steps.values())
        custom_data_df: "pd.DataFrame" = convert_custom_data(
            custom_data=self.custom_data,
            params_custom_list=params_custom_list,
            params_names=params_names,
        )

        new_values: list[list] = custom_data_df.values.tolist()
        new_values_tuple: list[tuple] = [tuple(el) for el in new_values]

        custom_data_df["custom_values"] = new_values_tuple
        params_custom_data_array: "xr.DataArray" = (
            custom_data_df.rename_axis(index="id")
            .to_xarray()
            .set_coords(params_names)["custom_values"]
        )

        return params_custom_data_array

    def _custom_parameters(
        self,
    ) -> Iterator[tuple[int, ParametersType]]:
        """Generate custom mode parameters based on input file.

        Yields
        ------
        index: int
        parameter_dict: dict
        """
        # Late import to speedup start-up time
        import pandas as pd

        if not isinstance(self.custom_data, pd.DataFrame):
            raise TypeError("Custom parameters not loaded from file.")

        index: int
        row_serie: pd.Series
        for index, row_serie in self.custom_data.iterrows():
            row: Sequence[Union[Number, str]] = row_serie.to_list()

            i: int = 0
            parameter_dict: ParametersType = {}
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

    def get_parameters_item(
        self, processor: "Processor"
    ) -> Sequence[Union[ParameterEntry, CustomParameterEntry]]:
        params_it = self._custom_parameters()

        return [
            CustomParameterEntry(index=index, parameters=parameter_dict, run_index=n)
            for n, (index, parameter_dict) in enumerate(params_it)
        ]


def short(s: str) -> str:
    """Split string with . and return the last element."""
    out = s.split(".")[-1]
    return out


def _get_short_name_with_model(name: str) -> str:
    _, _, model_name, _, param_name = name.split(".")

    return f"{model_name}.{param_name}"


def create_new_processor(
    processor: "Processor",
    parameter_dict: ParametersType,
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

    for key in parameter_dict:
        new_processor.set(key=key, value=parameter_dict[key])

    return new_processor
