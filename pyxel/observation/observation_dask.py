#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Subpackage for running Observation mode with Dask enabled."""

from collections.abc import Hashable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

import numpy as np

from pyxel.exposure import run_pipeline
from pyxel.observation import CustomMode, ProductMode, SequentialMode
from pyxel.pipelines import ResultId

if TYPE_CHECKING:
    import xarray as xr

    from pyxel.exposure import Readout
    from pyxel.outputs import ObservationOutputs, ValidFormat, ValidName
    from pyxel.pipelines import Processor


@dataclass
class VariableMetadata:
    """Store metadata for a Xarray data variable.

    Parameters
    ----------
    dims
        The dimensions of the data variable.
    attrs
        The attributes associated with the data variable.
    dtype
        The data type of the data variable.
    """

    dims: tuple[Hashable, ...]
    attrs: Mapping[str, Any]
    dtype: np.dtype


@dataclass
class CoordinateMetadata:
    """Store metadata for a coordinate in an Xarray Dataset.

    Parameters
    ----------
    data
        The data associated with the coordinates
    attrs
        The attributes of the coordinates
    """

    data: np.ndarray
    attrs: Mapping[str, Any]


@dataclass
class DatasetMetadata:
    """Store metadata for a Xarray dataset.

    It includes its dimensions, data variables, coordinates and attributes.

    Parameters
    ----------
    dims
        The dimension(s) of the dataset.
    data_vars
        Metadata for the data variables within the dataset.
    coords
        Metadata for the coordinates within the dataset.
    attrs
        Attributes associates with dataset.
    """

    dims: tuple[Hashable, ...]
    data_vars: Mapping[str, VariableMetadata]
    coords: Mapping[Hashable, CoordinateMetadata]
    attrs: Mapping[Hashable, Any]

    def to_coords(self) -> Mapping[Hashable, "xr.DataArray"]:
        # Late import to speedup start-up time
        import xarray as xr

        dct: dict[Hashable, xr.DataArray] = {}

        meta_coord: CoordinateMetadata
        for coord_name, meta_coord in self.coords.items():
            dct[coord_name] = xr.DataArray(
                meta_coord.data,
                dims=[coord_name],
                attrs=meta_coord.attrs,
            )

        return dct


def build_metadata(data_tree: "xr.DataTree") -> Mapping[str, DatasetMetadata]:
    """Construct metadata from a DataTree."""
    metadata = {}

    all_paths: Sequence[str] = sorted(data_tree.groups)

    for path in all_paths:
        sub_data_tree: "xr.DataTree" | "xr.DataArray" = data_tree[path]

        dims: tuple[Hashable, ...] = tuple(sub_data_tree.dims)

        metadata[path] = DatasetMetadata(
            dims=dims,
            data_vars={
                key: VariableMetadata(
                    dims=value.dims,
                    attrs=value.attrs,
                    dtype=value.dtype,
                )
                for key, value in sub_data_tree.data_vars.items()
                if (
                    path != "/bucket"
                    or (path == "/bucket" and {"y", "x"}.issubset(value.dims))
                )
            },
            coords={
                key: CoordinateMetadata(attrs=value.attrs, data=value.data)
                for key, value in sub_data_tree.coords.items()
            },
            attrs=sub_data_tree.attrs,
        )

    return metadata


def _get_output_core_dimensions(
    all_metadata: Mapping[str, DatasetMetadata],
) -> Sequence[tuple]:
    lst = []

    metadata: DatasetMetadata
    for metadata in all_metadata.values():
        if not metadata.data_vars:
            continue

        data_variable: VariableMetadata
        for data_variable in metadata.data_vars.values():
            lst.append(data_variable.dims)  # noqa: PERF401

    return lst


def _get_output_dtypes(
    all_metadata: Mapping[str, DatasetMetadata],
) -> Sequence[np.dtype]:
    lst = []

    metadata: DatasetMetadata
    for metadata in all_metadata.values():
        if not metadata.data_vars:
            continue

        data_variable: VariableMetadata
        for data_variable in metadata.data_vars.values():
            lst.append(data_variable.dtype)  # noqa: PERF401

    return lst


def _get_output_sizes(
    all_metadata: Mapping[str, DatasetMetadata],
) -> Mapping[Hashable, int]:
    """Retrieve the sizes our the output variables' dimensions from the metadata."""
    result: dict[Hashable, int] = {}

    metadata: DatasetMetadata
    for metadata_key, metadata in all_metadata.items():
        if not metadata.data_vars:
            continue

        coord_sizes: Mapping[Hashable, int] = {
            coord_key: len(meta_coords.data)
            for coord_key, meta_coords in metadata.coords.items()
        }

        for coord_key in coord_sizes:
            if coord_key in result and coord_sizes[coord_key] != coord_sizes[coord_key]:
                raise NotImplementedError(f"{metadata_key=}, {coord_key=}")

        result.update(coord_sizes)

    return result


def _run_pipelines_array_to_datatree(
    params_tuple: tuple,
    output_filenames: Sequence[str],
    params_index: int,
    dimension_names: Mapping[str, str],
    processor: "Processor",
    readout: "Readout",
    result_type: ResultId,
    pipeline_seed: int | None,
    progressbar: bool,
) -> "xr.DataTree":
    """Execute a single pipeline."""
    if len(dimension_names) != len(params_tuple):
        raise NotImplementedError

    # Create a new Processor object with modified parameters from dct
    # e.g. dct = {'pipeline.photon_collection.load_image.arguments.image_file': 'FITS/00001.fits'}
    dct: dict[str, tuple] = dict(zip(dimension_names, params_tuple, strict=False))
    new_processor: Processor = processor.replace(dct)

    # TODO: Move this to 'Processor' ? See #836
    new_readout: "Readout" = readout
    for key, value in dct.items():
        if key.startswith("observation.readout"):
            if key != "observation.readout.times":
                raise NotImplementedError(f"{key=}")

            new_readout = new_readout.replace(times=value)

    data_tree: "xr.DataTree" = run_pipeline(
        processor=new_processor,
        readout=new_readout,
        result_type=result_type,
        pipeline_seed=pipeline_seed,
        debug=False,  # Not supported in Observation mode
        with_inherited_coords=True,  # Must be set to True
        progressbar=progressbar,
    )

    # TODO: Remove this ! This should be done in
    # Save the outputs if configured
    if (
        processor.observation
        and processor.observation.outputs
        and processor.observation.outputs.save_data_to_file
    ):
        assert output_filenames  # TODO: improve this

        # TODO: use 'output_filenames' to get 'photon' or 'pixel' or ...
        # TODO: Get the last DataArray from: data_tree['/bucket/photon']
        # TODO: USe 'detector._header'

        result = processor.observation.outputs.save_to_files(
            processor=new_processor,
            filenames=output_filenames,
            header=new_processor.detector._header,
        )
        filenames_dct: Mapping[str, Mapping[str, str]] = (
            processor.observation.outputs.save_to_file(
                processor=new_processor,
                run_number=params_index,
            )
        )
    #
    #     datatree_dct: dict[str, xr.Dataset] = {}
    #     for name, partial_dct in filenames_dct.items():
    #         for file_formats, filename in partial_dct.items():
    #             datatree_dct[name] = xr.Dataset(
    #                 {file_formats: np.array(filename, dtype=np.object_)}
    #             )
    #
    #     data_tree["/output"] = DataTree.from_dict(datatree_dct)

    return data_tree


def _build_metadata(
    params_tuple: tuple,
    output_filenames: Sequence[str],
    dimension_names: Mapping[str, str],
    processor: "Processor",
    readout: "Readout",
    result_type: ResultId,
    pipeline_seed: int | None,
) -> Mapping[str, DatasetMetadata]:
    """Build metadata from a single pipeline run."""
    # TODO: Create a new temporary 'Output' (if needed) and remove it
    if processor.observation is None:
        raise NotImplementedError

    data_tree = _run_pipelines_array_to_datatree(
        params_tuple=params_tuple,
        output_filenames=output_filenames,
        params_index=0,
        dimension_names=dimension_names,
        processor=processor,
        readout=readout,
        result_type=result_type,
        pipeline_seed=pipeline_seed,
        progressbar=True,
    )

    return build_metadata(data_tree)


def _run_pipelines_tuple_to_array(
    params_tuple: tuple,
    params_index: int,
    dimension_names: Mapping[str, str],
    all_metadata: Mapping[str, DatasetMetadata],
    processor: "Processor",
    readout: "Readout",
    result_type: ResultId,
    pipeline_seed: int | None,
) -> tuple[np.ndarray, ...]:
    data_tree: "xr.DataTree" = _run_pipelines_array_to_datatree(
        params_tuple=params_tuple,
        params_index=params_index,
        dimension_names=dimension_names,
        processor=processor,
        readout=readout,
        result_type=result_type,
        pipeline_seed=pipeline_seed,
        progressbar=False,
    )

    # Convert the result from 'DataTree' to a tuple of numpy array(s)
    output_data: list[np.ndarray] = []

    metadata: DatasetMetadata
    for path, metadata in all_metadata.items():
        for key in metadata.data_vars:
            output_data.append(data_tree[f"{path}/{key}"].to_numpy())  # noqa: PERF401

    return tuple(output_data)


def _rebuild_datatree_from_dask(
    dask_dataarrays: tuple["xr.DataArray", ...],
    all_metadata: Mapping[str, DatasetMetadata],
) -> Mapping[str, Union["xr.Dataset", "xr.DataTree"]]:
    """Re-build a dictionary of Dask `Dataset` from a tuple of Dask `DataArrays`.

    Parameters
    ----------
    dask_dataarrays : tuple[DataArray, ...]
        A tuple of Dask-backed Xarray DataArrays which contain the (future) computed results.
    all_metadata : dict[str, DatasetMetaData]
        A dict that contains the metadata for each DataArrays. This includes dimensions, data variables,
        coordinates and attributes for each DataArrays in the structure.

    Returns
    -------
    dict[str, Union[Dataset, DataTree]]
        A dictionary where keys are paths and values are either Xarray Datasets or DataTree objects,
        rebuilt from the provided Dask DataArrays and metadata.
    """
    # Late import to speedup start-up time
    import xarray as xr

    # Rebuild the DataTree from 'all_dataarrays'
    dct: dict[str, xr.Dataset | xr.DataTree] = {}
    idx = 0
    path: str

    partial_metadata: DatasetMetadata
    for path, partial_metadata in all_metadata.items():
        if not partial_metadata.data_vars:
            # TODO: Use this ?
            # assert not partial_metadata.dims
            # assert not partial_metadata.coords

            empty_data_tree: xr.DataTree = xr.DataTree()
            empty_data_tree.attrs = dict(partial_metadata.attrs)

            dct[path] = empty_data_tree

        else:
            # assert partial_metadata.dims
            # assert partial_metadata.coords

            data_set = xr.Dataset(attrs=partial_metadata.attrs)

            var_name: str
            metadata_vars: VariableMetadata
            for var_name, metadata_vars in partial_metadata.data_vars.items():
                data_set[var_name] = (
                    dask_dataarrays[idx]
                    .rename(var_name)
                    .assign_attrs(metadata_vars.attrs)
                )

                idx += 1
                assert idx <= len(dask_dataarrays)

            coords: Mapping[Hashable, xr.DataArray] = partial_metadata.to_coords()
            dct[path] = data_set.assign_coords(coords)

    return dct


def _build_output_filenames(
    params_dataarray: "xr.DataArray",
    outputs: "ObservationOutputs",
) -> "xr.DataArray":
    """Generate output filenames as DataArray.

    Parameters
    ----------
    params_dataarray : DataArray
        DataArray containing parameter information for filenames.
    outputs : ObservationOutputs
        Object containing output folder and file-saving configuration.

    Returns
    -------
    DataArray
        DataArray with filenames as values and appropriate coordinates.

    Examples
    --------
    >>> params_dataarray
    <xarray.DataArray 'custom_values' (id: 6)> Size: 48B
    array([0, 1, 2, 3, 4, 5])
    Coordinates:
        image_file  (id) object 48B 'FITS/00001.fits' ... 'FITS/00006.fits'
      * id          (id) int64 48B 0 1 2 3 4 5
    >>> outputs
    Out[2]: ObservationOutputs<output_dir='./output/run_20241203_194724', num_files=1>

    >>> _build_output_filenames(params_dataarray=params_dataarray, outputs=outputs)
    xarray.DataArray (id: 6, name_ext: 1)> Size: 2kB
    array([['/Users/Frederic.Lemmel/sw/pyxel_dev/atreids/output/run_20241203_194724/detector_image_0.fits'],
           ['/Users/Frederic.Lemmel/sw/pyxel_dev/atreids/output/run_20241203_194724/detector_image_1.fits'],
           ['/Users/Frederic.Lemmel/sw/pyxel_dev/atreids/output/run_20241203_194724/detector_image_2.fits'],
           ['/Users/Frederic.Lemmel/sw/pyxel_dev/atreids/output/run_20241203_194724/detector_image_3.fits'],
           ['/Users/Frederic.Lemmel/sw/pyxel_dev/atreids/output/run_20241203_194724/detector_image_4.fits'],
           ['/Users/Frederic.Lemmel/sw/pyxel_dev/atreids/output/run_20241203_194724/detector_image_5.fits']],
          dtype='<U92')
    Coordinates:
      * id        (id) int64 48B 0 1 2 3 4 5
      * name_ext  (name_ext) <U10 40B 'image_fits'
    """
    # Late import to speedup start-up time
    import xarray as xr

    if outputs.save_data_to_file is None:
        raise NotImplementedError

    folder: Path = outputs.current_output_folder

    # Generate indices for the filename(s)
    # indices: xr.DataArray = params_dataarray.reset_coords(drop=True).rename("filename")
    # indices.values = np.arange(len(params_dataarray)).reshape(params_dataarray.shape)
    indices = xr.DataArray(
        np.arange(len(params_dataarray)).reshape(params_dataarray.shape),
        dims=params_dataarray.dims,
        coords=params_dataarray.coords,
        name="filename",
    )

    # Extract filename components from the outputs configuration
    filename_components: list[str] = []
    file_config: Mapping["ValidName", Sequence["ValidFormat"]]
    for file_config in outputs.save_data_to_file:
        name: str
        formats: Sequence[str]
        for name, formats in file_config.items():
            base_name: str = name.removeprefix("detector.").removesuffix(".array")

            for value in formats:
                filename_components.append(f"{base_name}_{value}")

    name_ext = xr.DataArray(
        filename_components,
        coords={"name_ext": filename_components},
    )

    # Define filename generation function
    def _generate_single_filename(index: int, name_ext: str, folder: str) -> str:
        bucket_name, extension = name_ext.split("_")
        return f"{folder}/detector_{bucket_name}_{index}.{extension}"

    # Use apply_ufunc for vectorized filename generation
    return xr.apply_ufunc(
        _generate_single_filename,
        indices,  # input parameter 'index'
        name_ext,  # input parameter 'name_ext'
        kwargs={"folder": folder},
        input_core_dims=[[], []],
        vectorize=True,
    )


def run_pipelines_with_dask(
    dim_names: Mapping[str, str],
    parameter_mode: ProductMode | SequentialMode | CustomMode,
    processor: "Processor",
    readout: "Readout",
    outputs: Optional["ObservationOutputs"],
    result_type: ResultId,
    pipeline_seed: int | None,
) -> "xr.DataTree":
    # Late import to speedup start-up time
    import xarray as xr

    # Get parameters as a DataArray
    params_dataarray: xr.DataArray = parameter_mode.create_params(dim_names=dim_names)

    # Get filenames with the same dimension as params_dataarray
    df_output_filenames: xr.DataArray | None = None
    if outputs:
        df_output_filenames = _build_output_filenames(
            params_dataarray=params_dataarray,
            outputs=outputs,
        )

    # Get the first parameter
    first_param: tuple = (
        params_dataarray.head(1)  # Get the first parameter
        .squeeze()  # Remove all dimensions of length 1
        .to_numpy()  # Convert to a numpy array
        .tolist()  # Convert to a tuple
    )

    # Get the first output filename
    first_output_filenames: Sequence[str] = []
    if df_output_filenames is not None:
        first_output_filenames = (
            df_output_filenames.isel(
                {key: 0 for key in df_output_filenames.dims if key != "name_ext"}
            )
            .to_numpy()
            .tolist()
        )

    # Extract metadata
    all_metadata: Mapping[str, DatasetMetadata] = _build_metadata(
        params_tuple=first_param,
        output_filenames=first_output_filenames,
        dimension_names=dim_names,
        processor=processor,
        readout=readout,
        result_type=result_type,
        pipeline_seed=pipeline_seed,
    )

    # Get the output core dimensions
    output_core_dims: Sequence[tuple] = _get_output_core_dimensions(all_metadata)

    # Get output sizes
    output_sizes: Mapping[Hashable, int] = _get_output_sizes(all_metadata)

    # Get output dtypes
    output_dtypes: Sequence[np.dtype] = _get_output_dtypes(all_metadata)

    # Coerce 'params_dataarray' to a Dask array
    params_dataarray_dask: xr.DataArray = params_dataarray.chunk(1)

    params_indexes: xr.DataArray = xr.zeros_like(params_dataarray)
    params_indexes[...] = np.arange(params_dataarray.size, dtype=int).reshape(
        params_indexes.shape
    )
    params_indexes_dask: xr.DataArray = params_indexes.chunk(1)

    # Create 'Dask' data arrays
    dask_dataarrays: tuple[xr.DataArray, ...] = xr.apply_ufunc(
        _run_pipelines_tuple_to_array,  # Function to apply
        params_dataarray_dask,  # Argument 'params_tuple'
        params_indexes_dask,  # Argument 'params_index'
        kwargs={  # other arguments
            "dimension_names": dim_names,
            "processor": processor,
            "all_metadata": all_metadata,
            "readout": readout,
            "result_type": result_type,
            "pipeline_seed": pipeline_seed,
        },
        input_core_dims=[[], []],
        output_core_dims=output_core_dims,
        vectorize=True,  # loop over non-core dims
        dask="parallelized",
        dask_gufunc_kwargs={"output_sizes": output_sizes},
        output_dtypes=output_dtypes,  # TODO: Move this to 'dask_gufunc_kwargs'
    )

    # Rebuild a DataTree from 'dask_dataarrays'
    dct: Mapping[str, xr.Dataset | xr.DataTree] = _rebuild_datatree_from_dask(
        dask_dataarrays=dask_dataarrays,
        all_metadata=all_metadata,
    )

    # Please note that at this stage the datatree does not contain node '/output'.
    # This node is added later
    final_datatree = xr.DataTree.from_dict(dct)

    if "observation.readout.times" in dim_names:
        # TODO: See #836
        final_datatree["/bucket"] = (
            final_datatree["/bucket"]
            .squeeze("time", drop=True)  # Remove dimension 'time'
            .rename(readout_time="time")  # Rename dimension 'readout' to 'time
        )

        final_datatree["/bucket/time"].attrs = {
            "units": "s",
            "long_name": "Readout time",
        }

    # TODO: Fix this. See issue #723
    if outputs and outputs.save_data_to_file:
        # Late import
        from pyxel.outputs.outputs import save_datatree

        data_tree_filenames: "xr.DataTree" | None = save_datatree(
            data_tree=final_datatree.isel(time=-1),
            outputs=outputs.save_data_to_file,
            current_output_folder=outputs.current_output_folder,
            with_inherited_coords=True,
        )

        final_datatree["/output"] = data_tree_filenames

    return final_datatree
