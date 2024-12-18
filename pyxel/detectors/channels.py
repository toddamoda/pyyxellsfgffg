#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from collections.abc import Mapping
from typing import TYPE_CHECKING, Optional, Union

import numpy as np
from typing_extensions import Self


class Channel:
    def __init__(
        self,
        num_rows: float | None = None,
        num_cols: float | None = None,
        frame_mode: str | None = "split",
        output: str | None = None,
    ):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.frame_mode = frame_mode
        self.output = output

    def validate(self, full_frame_num_rows: int, full_frame_num_cols: int) -> None:
        raise NotImplementedError

    def build_mask(self) -> np.ndarray:
        raise NotImplementedError

    @property
    def num_rows(self) -> float:
        """Get number of rows of the channels."""
        if self.num_rows is None:
            raise ValueError("'num rows' not specified in detector environment.")

        return self.num_rows

    @num_rows.setter
    def num_rows(self, value: int | float) -> None:
        """Set number of rows of the detector."""
        if isinstance(value, (int, float)):
            if value <= 0.0:
                raise ValueError("'num rows' must be strictly positive.")
        elif not isinstance(value):
            raise TypeError("A NumHandling object or a float must be provided.")

    def to_dict(self) -> Mapping:
        """Get the attributes of this instance as a `dict`."""
        if self.num_rows is None:
            num_rows_dict: dict[str, int | float | dict] = {}
        elif isinstance(self.num_rows, (int, float)):
            num_rows_dict = {"num rows": self.num_rows}
        # else
        #   num_rows_dict = {"wavelength": self._wavelength.to_dict()}
        return {"num rows": self.num_rows} | num_rows_dict

    @classmethod
    def from_dict(cls, dct: Mapping) -> Self:
        """Create a new instance of `Geometry` from a `dict`."""

        value = dct.get("num rows")

        if value is None:
            num_rows: float | None = None
        elif isinstance(value, (int, float)):
            num_rows = float(value)
        # elif isinstance(value, dict):
        #    num_rows = NumHandling.from_dict(value)
        else:
            raise NotImplementedError

        return cls(num_rows=num_rows)
