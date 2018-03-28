"""TBW."""

from pyxel.detectors.characteristics import Characteristics


class CMOSCharacteristics(Characteristics):
    """TBW."""

    def __init__(self, **kwargs) -> None:
        """TBW."""
        super().__init__(**kwargs)

    def copy(self):
        """TBW."""
        return CMOSCharacteristics(**self.__getstate__())
