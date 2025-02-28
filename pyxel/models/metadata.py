#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Sub-package for metadata."""

from collections.abc import Callable
from dataclasses import dataclass

from typing_extensions import Protocol

from pyxel.detectors import Detector


@dataclass(frozen=True, slots=True)
class Metadata:
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


class ModelCallable(Protocol):
    """Define a callable protocol for a model."""

    def __call__(self, detector: Detector, **kwargs) -> None: ...


class ModelCallableWithMetaData(Protocol):
    """Define a callable protocol for a model with metadata information."""

    meta: Metadata | None = None

    def __call__(self, detector: Detector, **kwargs) -> None: ...


def attach_metadata(func: Callable) -> ModelCallableWithMetaData:
    """Define a decorator to add metadata to a model.

    Examples
    --------
    >>> from pyxel.detectors import Detector
    >>> from pyxel.models import attach_metadata, Metadata

    >>> def my_model(detector: Detector, param1: int, param2: str) -> None:
    ...     pass  # Do something

    >>> my_model.meta = Metadata(description="foo", config="bar")
    """
    meta: Metadata | None = None

    func.meta = meta  # type: ignore[attr-defined]
    return func  # type: ignore[return-value]
