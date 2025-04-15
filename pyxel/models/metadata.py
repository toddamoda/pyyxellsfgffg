#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Sub-package for metadata."""

from dataclasses import dataclass
from typing import Literal

from typing_extensions import Protocol

from pyxel.detectors import Detector


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
class History:  # noqa: D101
    version: str | None = None


@dataclass(frozen=True, slots=True)
class Metadata:  # noqa: D101
    name: str
    model_group: Literal[
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
    version: str | None = None
    detector: list[str] | str = "all"
    status: Literal["draft", "validated", "deprecated"] | None = None
    model: MetadataModel | None = None
    authors: list[str] | str | None = None
    notebooks: list[str] | str | None = None
    references: list[str] | None = None
    history: list[History] | None = None


class ModelCallable(Protocol):
    """Define a callable protocol for a model."""

    def __call__(self, detector: Detector, **kwargs) -> None: ...


class ModelCallableWithMetaData(Protocol):
    """Define a callable protocol for a model with metadata information."""

    meta: Metadata | None = None

    def __call__(self, detector: Detector, **kwargs) -> None: ...
