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


# --------------------- new helper for clarity ---------------------
def _inject_readout_times_into_detector(processor: "Processor", readout: "Readout") -> None:
    """
    Inject the readout times array into the detector so photon models
    can access it (e.g. for time-dependent photon integration).
    """
    if not hasattr(processor, "detector"):
        return

    detector = processor.detector
    try:
        # Extract readout times from Readout config (if available)
        if hasattr(readout, "times") and readout.times is not None:
            detector.readout_times = np.asarray(readout.times)
        else:
            # Derive simple times from exposure time if not explicitly given
            t_end = getattr(readout, "exposure_time", None)
            if t_end is not None:
                detector.readout_times = np.linspace(0, t_end, num=2)
    except Exception as err:
        # This must not block observation; log or note in debug mode
        if sys.version_info >= (3, 11):
            err.add_note("Unable to inject 'readout_times' into detector.")
        raise


def explain_invalid_key(invalid_key: str, valid_keys: list[str]) -> str:
    parts = invalid_key.split(".")
    path_so_far = []

    for part in parts:
        path_so_far.append(part)
        current = ".".join(path_so_far)
        if not any(key.startswith(current) for key in valid_keys):
            pointer_pos = (
                len("Missing parameter: '")
                + len(".".join(path_so_far[:-1]))
                + (1 if path_so_far[:-1] else 0)
            )
            pointer_line = " " * pointer_pos + "^" * len(part)
            return (
                f"Missing parameter: '{invalid_key}'\n"
                f"{pointer_line}\n"
                f"{' ' * pointer_pos}Non-existing parameter"
            )
    return f"Missing parameter: '{invalid_key}'"


# unchanged helper functions...
# (keep _get_short_dimension_names_new, build_parameter_mode etc.)


class Observation:
    """Observation class."""

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

    # --- unchanged properties ---

    def _get_parameter_types(self) -> Mapping[str, ParameterType]:
        for step in self.parameter_mode.enabled_steps:
            self.parameter_types.update({step.key: step.type})
        return self.parameter_types

    # --- core modification: inject readout times before pipeline run ---
    def run_pipelines(
        self,
        processor: Processor,
        with_inherited_coords: bool,
    ) -> "xr.DataTree":
        """Run the observation pipelines and return a `DataTree` object."""
        import xarray as xr
        from tqdm.auto import tqdm

        self.validate_steps(processor)

        types: Mapping[str, ParameterType] = self._get_parameter_types()
        dim_names: Mapping[str, str] = _get_short_dimension_names_new(types)

        # inject readout time vector for downstream models
        _inject_readout_times_into_detector(processor, self.readout)

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
                parameters = self.parameter_mode.get_parameters_item(processor=processor)

            datatree_list: Sequence["xr.DataTree"] = []
            for el in tqdm(parameters):
                # create new processor instance
                new_processor = create_new_processor(processor=processor, parameter_dict=el.parameters)

                # ensure every processor has the readout times available
                _inject_readout_times_into_detector(new_processor, self.readout)

                datatree_list.append(
                    self._run_single_pipeline(
                        el,
                        dimension_names=dim_names,
                        processor=new_processor,
                        types=types,
                        with_inherited_coords=with_inherited_coords,
                    )
                )

            final_datatree = xr.map_over_datasets(
                lambda *data: xr.merge(data, join="outer", compat="no_conflicts"),
                *datatree_list,
            )

        parameter_name: str = str(self.parameter_mode.__class__)
        final_datatree.attrs["running mode"] = f"Observation - {parameter_name}"
        return final_datatree

    # rest of the file (validate_steps, _run_single_pipeline, _add_custom_parameters, _add_product_parameters)
    # stays the same
