#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Sampling detector properties class."""

from collections.abc import Sequence
from typing import Union

import numpy as np

from pyxel.exposure.readout import calculate_steps


class ReadoutProperties:
    """Readout sampling detector properties.

    Parameters
    ----------
    times : Sequence[Number]
        A sequence of numeric values representing the sampling times for the readout simulation.
    start_time : float, optional. Default: 0.0
        A float representing the starting time of the readout simulation.
        The readout time(s) should be greater that this ``start_time``.
    non_destructive : bool, optional. Default: False
        A boolean flag indicating whether the readout simulation is non-destructive.
        If set to ``True``, the readout process will not modify the underlying data.

    Examples
    --------
    >>> readout_properties = ReadoutProperties(times=[1, 2, 4, 7, 10], start_time=0.0)
    >>> readout_properties.times
    array([ 1.,  2.,  4.,  7., 10.])
    >>> readout_properties.steps
    array([0., 1., 2., 3., 3.])
    >>> readout_properties.num_steps
    5
    >>> readout.absolute_time
    0.0
    """

    def __init__(
        self,
        times: Union[Sequence[float], np.ndarray],
        start_time: float = 0.0,
        non_destructive: bool = False,
    ):
        times_1d = np.array(times, dtype=float)
        assert times_1d.ndim == 1

        steps = calculate_steps(times=times_1d, start_time=start_time)

        self._times: np.ndarray = times_1d
        self._steps: np.ndarray = steps

        self._times.flags.writeable = False
        self._steps.flags.writeable = False

        # Fixed at beginning
        self._num_steps: int = len(self._steps)
        self._start_time: float = start_time
        self._end_time: float = self._times[-1]
        self._non_destructive: bool = non_destructive
        self._times_linear: bool = bool(np.all(self._steps == self._steps[0]))

        # Changing
        self._time: float = 0.0
        self._time_step: float = 1.0
        self._read_out: bool = True
        self._pipeline_count: int = 0

    @property
    def times(self) -> np.ndarray:
        """Return readout times."""
        return self._times

    @property
    def steps(self) -> np.ndarray:
        """Return time steps between consecutive readout times."""
        return self._steps

    @property
    def num_steps(self) -> int:
        """TBW."""
        return self._num_steps

    @property
    def start_time(self) -> float:
        """TBW."""
        return self._start_time

    @start_time.setter
    def start_time(self, value: float) -> None:
        """TBW."""
        self._start_time = value

    @property
    def end_time(self) -> float:
        """TBW."""
        return self._end_time

    @property
    def non_destructive(self) -> bool:
        """TBW."""
        return self._non_destructive

    @property
    def times_linear(self) -> bool:
        """TBW."""
        return self._times_linear

    @property
    def time(self) -> float:
        """TBW."""
        return self._time

    @time.setter
    def time(self, value: float) -> None:
        """TBW."""
        self._time = value

    @property
    def absolute_time(self) -> float:
        """TBW."""
        return self._start_time + self._time

    @property
    def time_step(self) -> float:
        """TBW."""
        return self._time_step

    @time_step.setter
    def time_step(self, value: float) -> None:
        """TBW."""
        self._time_step = value

    @property
    def read_out(self) -> bool:
        """TBW."""
        return self._read_out

    @read_out.setter
    def read_out(self, value: bool) -> None:
        """TBW."""
        self._read_out = value

    @property
    def pipeline_count(self) -> int:
        """TBW."""
        return self._pipeline_count

    @pipeline_count.setter
    def pipeline_count(self, value: int) -> None:
        """TBW."""
        self._pipeline_count = value

    @property
    def is_first_readout(self) -> bool:
        """Check if this is the first readout time."""
        return bool(self.pipeline_count == 0)

    @property
    def is_last_readout(self) -> bool:
        """Check if this is the last readout time."""
        return bool(self.pipeline_count == (self.num_steps - 1))
