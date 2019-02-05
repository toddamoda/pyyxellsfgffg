"""TBW."""
import itertools
import typing as t
from copy import deepcopy
import numpy as np
from esapy_config import eval_range, get_obj_att, get_value


class StepValues:
    """TBW."""

    def __init__(self, key, values,
                 enabled=True, current=None):
        """TBW.

        :param key:
        :param values:
        :param enabled:
        :param current:
        """
        # TODO: should the values be evaluated?
        self.key = key                              # unique identifier to the step. example: detector.geometry.row
        self.values = values                        # type: t.List[t.Union[float, int]]
        self.enabled = enabled                      # type: bool
        self.current = current

    def __getstate__(self):
        """TBW."""
        return {
            'key': self.key,
            'values': self.values,
            'enabled': self.enabled,
            'current': self.current,
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


class ParametricAnalysis:
    """TBW."""

    def __init__(self,
                 parametric_mode,
                 steps: t.List[StepValues],
                 from_file: str = None,
                 column_range: t.List[int] = None) -> None:
        """TBW."""
        self.parametric_mode = parametric_mode
        self.steps = steps
        self.file = from_file
        self.data = None
        if column_range:
            self.columns = slice(column_range[0], column_range[1])

    def __getstate__(self):
        """TBW."""
        return {'mode': self.parametric_mode,
                'steps': self.steps}

    @property
    def enabled_steps(self):
        """TBW."""
        return [step for step in self.steps if step.enabled]

    def _parallel(self, processor):
        """TBW.

        :param processor:
        :return:
        """
        self.data = np.loadtxt(self.file)[:, self.columns]
        for data_array in self.data:
            i = 0
            new_proc = deepcopy(processor)
            for step in self.enabled_steps:
                key = step.key
                if step.values == '_':
                    value = data_array[i]
                    i += 1
                elif isinstance(step.values, list) and all(x == '_' for x in step.values[:]):
                    value = data_array[i: i + len(step.values)]
                    i += len(value)
                else:
                    raise ValueError('Character "_" (or a list of it) should be used to '
                                     'indicate parameters updated in parallel')
                new_proc.set(key, value)
            yield new_proc

    def _sequential(self, processor):
        """TBW.

        :param processor:
        :return:
        """
        for step in self.enabled_steps:
            key = step.key
            for value in step:
                step.current = value
                new_proc = deepcopy(processor)
                new_proc.set(key, value)
                yield new_proc

    def _embedded(self, processor):
        """TBW.

        :param processor:
        :return:
        """
        all_steps = self.enabled_steps
        keys = [step.key for step in self.enabled_steps]
        for params in itertools.product(*all_steps):
            new_proc = deepcopy(processor)
            for key, value in zip(keys, params):
                for step in all_steps:
                    if step.key == key:
                        step.current = value
                new_proc.set(key=key, value=value)
            yield new_proc

    def collect(self, processor):
        """TBW."""
        for step in self.enabled_steps:
            key = step.key
            if 'pipeline.' in key:
                model_name = key[:key.find('.arguments')]
                model_enabled = model_name + '.enabled'
                if not processor.get(model_enabled):
                    raise ValueError('The "%s" model referenced in parametric configuration '
                                     'has not been enabled in yaml config!' % model_name)

        if self.parametric_mode == 'embedded':
            configs = self._embedded(processor)
        elif self.parametric_mode == 'sequential':
            configs = self._sequential(processor)
        elif self.parametric_mode == 'parallel':
            configs = self._parallel(processor)
        else:
            configs = []

        return configs

    def debug(self, processor):
        """TBW."""
        result = []
        configs = self.collect(processor)
        for i, config in enumerate(configs):
            values = []
            for step in self.enabled_steps:
                _, att = get_obj_att(config, step.key)
                value = get_value(config, step.key)
                values.append((att, value))
            print('%d: %r' % (i, values))
            result.append((i, values))
        return result


class Configuration:
    """TBW."""

    def __init__(self, mode,
                 parametric=None,
                 calibration=None
                 ) -> None:
        """TBW.

        :param mode:
        :param parametric:
        :param calibration:
        """
        self.mode = mode
        self.parametric = parametric
        self.calibration = calibration
