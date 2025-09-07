#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Parametric mode class and helper functions."""

import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional

import numpy as np

import pyxel
from pyxel.exposure import Readout, run_pipeline
from pyxel.observation import (
    CustomMode,
    CustomParameterEntry,
    ParameterEntry,
    ParametersType,
    ParameterType,
    ParameterValues,
    ProductMode,
    SequentialMode,
    _get_short_name_with_model,
    create_new_processor,
    run_pipelines_with_dask,
    short,
)
from pyxel.pipelines import Processor, ResultId, get_result_id

if TYPE_CHECKING:
    import xarray as xr
    from pyxel.outputs import ObservationOutputs


# 🌟 NEW: Friendly error explainer
def explain_invalid_key(invalid_key: str, valid_keys: list[str]) -> str:
    parts = invalid_key.split(".")
    path_so_far = []

    for part in parts:
        path_so_far.append(part)
        current = ".".join(path_so_far)
        if not any(key.startswith(current) for key in valid_keys):
            pointer_pos = len("Missing parameter: '") + len(".".join(path_so_far[:-1])) + (1 if path_so_far[:-1] else 0)
            pointer_line = " " * pointer_pos + "^" * len(part)
            return (
                f"Missing parameter: '{invalid_key}'\n"
                f"{pointer_line}\n"
                f"{' ' * pointer_pos}Non-existing parameter"
            )

    return f"Missing parameter: '{invalid_key}'"


def _get_short_dimension_names_new(
    types: Mapping[str, ParameterType],
) -> Mapping[str, str]:
    potential_dim_names: dict[str, str] = {}
    for param_name in types:
        if param_name == "observation.readout.times":
            short_name: str = "readout_time"
        else:
            short_name = short(param_name)

        potential_dim_names[param_name] = short_name

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


def build_parameter_mode(
    mode: Literal["product", "sequential", "custom"],
    parameters: Sequence[ParameterValues],
    custom_filename: str | None = None,
    column_range: tuple[int, int] | None = None,
) -> ProductMode | SequentialMode | CustomMode:
    match mode:
        case "product":
            return ProductMode(parameters)

        case "sequential":
            return SequentialMode(parameters)

        case "custom":
            custom_columns: slice | None = (
                slice(*column_range) if column_range else None
            )
            assert custom_filename is not None

            return CustomMode.build(
                parameters,
                custom_file=custom_filename,
                custom_columns=custom_columns,
            )

        case _:
            raise NotImplementedError


class Observation:
    def __init__(
        self,
        parameters: Sequence[ParameterValues],
        outputs: Optional["ObservationOutputs"] = None,
        readout: Readout | None = None,
        mode: Literal["product", "sequential", "custom"] = "product",
        from_file: str | None = None,
        column_range: tuple[int, int] | None = None,
        with_dask: bool = False,
        result_type: str = "all",
        pipeline_seed: int | None = None,
        working_directory: str | None = None,
    ):
        self.outputs: "ObservationOutputs" | None = outputs
        self.readout: Readout = readout or Readout()

        self.parameter_mode: ProductMode | SequentialMode | CustomMode = (
            build_parameter_mode(
                mode=mode,
                parameters=parameters,
                custom_filename=from_file,
                column_range=column_range,
            )
        )

        self.working_directory: Path | None = (
            Path(working_directory) if working_directory else None
        )

        pyxel.set_options(working_directory=self.working_directory)

        self.with_dask = with_dask
        self.parameter_types: dict[str, ParameterType] = {}
        self._result_type: ResultId = get_result_id(result_type)
        self._pipeline_seed = pipeline_seed

    def __repr__(self):
        cls_name: str = self.__class__.__name__
        return f"{cls_name}<mode={self.parameter_mode!s}, num_parameters={len(self.parameter_mode.parameters)}>"

    @property
    def result_type(self) -> ResultId:
        return self._result_type

    @result_type.setter
    def result_type(self, value: ResultId) -> None:
        self._result_type = get_result_id(value)

    @property
    def pipeline_seed(self) -> int | None:
        return self._pipeline_seed

    @pipeline_seed.setter
    def pipeline_seed(self, value: int) -> None:
        self._pipeline_seed = value

    def _get_parameter_types(self) -> Mapping[str, ParameterType]:
        for step in self.parameter_mode.enabled_steps:
            self.parameter_types.update({step.key: step.type})
        return self.parameter_types

    def validate_steps(self, processor: Processor) -> None:
        step: ParameterValues
        for step in self.parameter_mode.enabled_steps:
            key: str = step.key
            if not processor.has(key):
                valid_keys = list(processor.steps.keys())
                message = explain_invalid_key(key, valid_keys)
                raise KeyError(message)

            if "pipeline." in key:
                model_name: str = key[: key.find(".arguments")]
                model_enabled: str = model_name + ".enabled"
                if not processor.get(model_enabled):
                    raise ValueError(
                        f"The '{model_name}' model referenced in Observation "
                        "configuration has not been enabled in yaml config!"
                    )

            if any(x == "_" for x in step.values[:]) and not isinstance(
                self.parameter_mode, CustomMode
            ):
                raise ValueError(
                    "Either define 'custom' as parametric mode or "
                    "do not use '_' character in 'values' field"
                )

    def run_pipelines(
        self,
        processor: Processor,
        with_inherited_coords: bool,
    ) -> "xr.DataTree":
        import xarray as xr
        from tqdm.auto import tqdm

        self.validate_steps(processor)

        types: Mapping[str, ParameterType] = self._get_parameter_types()
        dim_names: Mapping[str, str] = _get_short_dimension_names_new(types)

        if self.with_dask:
            if with_inherited_coords is False:
                raise NotImplementedError

            final_datatree: "xr.DataTree" = run_pipelines_with_dask(
                dim_names=dim_names,
                parameter_mode=self.parameter_mode,
                processor=processor,
                readout=self.readout,
                outputs=self.outputs,
                pipeline_seed=self.pipeline_seed,
            )

        else:
            if isinstance(self.parameter_mode, ProductMode):
                parameters = self.parameter_mode.get_parameters_item()
            else:
                parameters = self.parameter_mode.get_parameters_item(
                    processor=processor
                )

            datatree_list: Sequence["xr.DataTree"] = [
                self._run_single_pipeline(
                    el,
                    dimension_names=dim_names,
                    processor=processor,
                    types=types,
                    with_inherited_coords=with_inherited_coords,
                )
                for el in tqdm(parameters)
            ]

            final_datatree = xr.map_over_datasets(
                lambda *data: xr.merge(data), *datatree_list
            )

        parameter_name: str = str(self.parameter_mode.__class__)
        final_datatree.attrs["running mode"] = f"Observation - {parameter_name}"

        return final_datatree

    def _run_single_pipeline(
        self,
        param_item: ParameterEntry | CustomParameterEntry,
        dimension_names: Mapping[str, str],
        processor: Processor,
        types: Mapping[str, ParameterType],
        with_inherited_coords: bool,
        with_outputs: bool = True,
        with_extra_dims: bool = True,
    ) -> "xr.DataTree":
        new_processor = create_new_processor(
            processor=processor,
            parameter_dict=param_item.parameters,
        )

        try:
            data_tree: "xr.DataTree" = run_pipeline(
                processor=new_processor,
                readout=self.readout,
                outputs=self.outputs,
                pipeline_seed=self.pipeline_seed,
                debug=False,
                with_inherited_coords=with_inherited_coords,
            )
        except Exception as exc:
            if sys.version_info >= (3, 11):
                exc.add_note(
                    "This error occurred in 'Observation' mode with the following parameters:"
                )
                for key, value in param_item.parameters.items():
                    exc.add_note(f"  - {key!r}: {value!r}")
            raise

        if with_outputs and self.outputs:
            data_tree["/output"] = self.outputs.save_to_file(
                processor=new_processor,
                run_number=param_item.run_index,
            )

        if not with_extra_dims:
            return data_tree

        if isinstance(param_item, ParameterEntry):
            return _add_product_parameters(
                data_tree, param_item.parameters, param_item.index,
                dimension_names, types
            )

        return _add_custom_parameters(
            data_tree, param_item.parameters, param_item.index,
            dimension_names, types
        )


# _add_custom_parameters and _add_product_parameters remain unchanged from your version
# Let me know if you’d like me to include those too for completeness 🌼
