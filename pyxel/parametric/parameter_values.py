"""TBW."""
import typing as t
from esapy_config import eval_range


class ParameterValues:
    """TBW."""

    def __init__(self,
                 key: str, values,
                 enabled: bool = True,
                 current=None,
                 logarithmic: bool = False,
                 boundaries: list = None):
        """TBW.

        :param key:
        :param values:
        :param enabled:
        :param current:
        :param logarithmic:
        :param boundaries:
        """
        # TODO: should the values be evaluated?
        self.key = key                              # unique identifier to the step. example: detector.geometry.row
        self.values = values                        # type: t.List[t.Union[float, int]]
        self.enabled = enabled                      # type: bool
        self.current = current
        self.logarithmic = logarithmic              # type: bool
        self.boundaries = boundaries                # type: t.Optional[list]

    def __getstate__(self):
        """TBW."""
        return {
            'key': self.key,
            'values': self.values,
            'enabled': self.enabled,
            'current': self.current,
            'logarithmic': self.logarithmic,
            'boundaries': self.boundaries,
        }

    def __len__(self):
        """TBW."""
        values = eval_range(self.values)
        return len(values)

    def __iter__(self):
        """TBW."""
        values = eval_range(self.values)
        for value in values:
            yield value
