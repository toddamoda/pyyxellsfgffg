#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Sub-package for metadata."""

import difflib
import importlib
from collections import defaultdict
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal, TypeAlias, get_args

from typing_extensions import Protocol

from pyxel.detectors import Detector

# Define all allowed Pyxel model groups as literal strings
ModelGroupsType: TypeAlias = Literal[
    "Scene Generation",
    "Photon Collection",
    "Charge Generation",
    "Charge Collection",
    "Phasing",
    "Charge Transfer",
    "Charge Measurement",
    "Readout Electronics",
    "Data Processing",
]

# Global registry that stores all registered model metadata, grouped by model type
REGISTERED_METADATA: Mapping[ModelGroupsType, list["Metadata"]] = defaultdict(list)


class MetadataGroup(Mapping[str, "Metadata"]):
    """Read-only mapping of model names to their metadata withing a model group.

    Notes
    -----
    This class automatically imports the corresponding sub-package model group from `pyxel.models`
    to ensure all models from the given group have their metadata registered.

    Parameters
    ----------
    group_name : ModelGroupsType
        The name of the model group (e.g., 'Photon Collection')
    """

    def __init__(self, group_name: ModelGroupsType):
        # TODO: Find a better way to get the package based on the name of the model group.
        # Extract sub-package name from 'group_name' (e.g. 'Photon Collection' becomes 'photon_collection')
        package_name: str = group_name.lower().replace(" ", "_")

        self._module_name: str = f"pyxel.models.{package_name}"

        # Dynamically import 'package_name' to force auto registration of all models from this 'group_name'
        _ = importlib.import_module(name=self._module_name)

        all_metadata: Sequence["Metadata"] = REGISTERED_METADATA.get(group_name, list())
        self._group_metadata: Mapping[str, "Metadata"] = {
            metadata.name: metadata for metadata in all_metadata
        }

    def __repr__(self) -> str:
        cls_name: str = self.__class__.__name__
        return f"{cls_name}<{len(self)} models in {self._module_name!r}>"

    def __getitem__(self, item: Any) -> "Metadata":
        if item not in self._group_metadata:
            all_matches: Sequence[str] = difflib.get_close_matches(
                word=str(item),
                possibilities=list(self),
            )

            match all_matches:
                case [close_match, *_]:
                    raise KeyError(
                        f"Model {item!r} not found in module {self._module_name!r}. "
                        f"Did you mean {close_match!r}?"
                    )
                case _:
                    raise KeyError(
                        f"Model {item!r} not found in module {self._module_name!r}."
                    )

        return self._group_metadata[item]

    def __iter__(self) -> Iterator[str]:
        return iter(self._group_metadata)

    def __len__(self) -> int:
        return len(self._group_metadata)


class MetadataAll(Mapping[ModelGroupsType, MetadataGroup]):
    """Read-only mapping of all metadata for all model groups.

    Examples
    --------
    >>> metadata = MetadataAll()
    >>> metadata
    MetadataAll<9 groups>
    >>> list(metadata)
    ['Scene Generation',
     'Photon Collection',
     'Charge Generation',
     'Charge Collection',
     'Phasing',
     'Charge Transfer',
     'Charge Measurement',
     'Readout Electronics',
     'Data Processing']

    >>> metadata["Charge Collection"]
    MetadataGroup<6 models>

    >>> list(metadata["Charge Collection"])
    ['simple_collection',
     'fixed_pattern_noise',
     'simple_full_well',
     'simple_ipc',
     'simple_persistence',
     'persistence']

     >>> metadata["Charge Collection"]["simple_collection"]
     Metadata(name='simple_collection', model_group='Charge Collection', version=None, detector='all', status=None, ...)
    """

    def __init__(self):
        self._all_groups: Sequence[ModelGroupsType] = get_args(ModelGroupsType)

    def __repr__(self) -> str:
        cls_name: str = self.__class__.__name__

        return f"{cls_name}<{len(self)} groups>"

    def __getitem__(self, item: Any) -> MetadataGroup:
        if item not in self._all_groups:
            all_matches: Sequence[str] = difflib.get_close_matches(
                word=str(item),
                possibilities=list(self),
                cutoff=0.3,
            )

            match all_matches:
                case [close_match, *_]:
                    raise KeyError(
                        f"Model Group {item!r} not found. Did you mean {close_match!r}?"
                    )

                case _:
                    raise KeyError(f"Model Group {item!r} not found.")

        return MetadataGroup(item)

    def __iter__(self) -> Iterator[ModelGroupsType]:
        return iter(self._all_groups)

    def __len__(self) -> int:
        return len(self._all_groups)


@dataclass(frozen=True, slots=True)
class MetadataModel:
    """Store metadata information for the models.

    Attributes
    ----------
    description : str
        A detailed explanation of the model written in Markdown language.
    config : str
        Example of YAML configuration snipped to use with the model.
    references : list of str, optional
        List of references for the model.
    notebooks : list of str, optional
        List of Jupyter notebooks demonstrating the model.
    """

    description: str
    config: str
    references: list[str] | None = None
    notebooks: list[str] | None = None


@dataclass(frozen=True, slots=True)
class History:
    """Store version history information for a Pyxel model."""

    version: str | None = None


@dataclass(frozen=True, slots=True)
class Metadata:
    """Store complete metadata associate to a Pyxel's model."""

    name: str
    model_group: ModelGroupsType
    version: str | None = None
    detector: list[str] | str = "all"
    status: Literal["draft", "validated", "deprecated"] | None = None
    model: MetadataModel | None = None
    authors: list[str] | str | None = None
    notebooks: list[str] | str | None = None
    references: list[str] | None = None
    history: list[History] | None = None

    def __post_init__(self):
        # Automatic registration when creating a new 'MetaData' object
        REGISTERED_METADATA[self.model_group].append(self)


class ModelCallable(Protocol):
    """Define a callable protocol for a model."""

    def __call__(self, detector: Detector, **kwargs) -> None: ...


class ModelCallableWithMetaData(Protocol):
    """Define a callable protocol for a model with metadata information."""

    meta: Metadata | None = None

    def __call__(self, detector: Detector, **kwargs) -> None: ...
