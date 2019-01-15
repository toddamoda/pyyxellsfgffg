"""Pyxel Array class."""
import numpy as np
import typing as t  # noqa: F401
from astropy.units import cds
cds.enable()


class Array:
    """Array class."""

    def __init__(self) -> None:
        """TBW."""
        self.type = None            # type: t.Optional[type]
        self.exp_type = None        # type: t.Optional[type]
        self.type_list = None       # type: t.Optional[t.List[type]]
        self._array = None          # type: t.Optional[np.ndarray]

    @property
    def array(self):
        """Two dimensional numpy array storing the data."""
        return self._array.astype(self.type)

    @array.setter
    def array(self, value):
        """
        Overwrite the two dimensional numpy array storing the data.

        Only accepts an array with the right type and shape.
        """
        if isinstance(value, np.ndarray):
            if value.dtype in self.type_list:
                if value.shape == self._array.shape:
                    self.type = value.dtype
                    self._array = value
                else:
                    raise ValueError('Shape of %s array should be %s' %
                                     (self.__class__.__name__, str(self._array.shape)))
            else:
                raise TypeError('Type of %s array should be a(n) %s' %
                                (self.__class__.__name__, self.exp_type.__name__))
        else:
            raise TypeError('%s array should be a numpy.ndarray' % self.__class__.__name__)
