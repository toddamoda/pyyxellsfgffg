"""TBW."""
import itertools
import typing as t
import numpy as np
from copy import deepcopy
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
                 steps: t.List[StepValues]
                 ) -> None:
        """TBW."""
        self.parametric_mode = parametric_mode
        self.steps = steps

    def __getstate__(self):
        """TBW."""
        return {'mode': self.parametric_mode,
                'steps': self.steps}

    @property
    def enabled_steps(self):
        """TBW."""
        return [step for step in self.steps if step.enabled]

    def _image_generator(self, processor):
        """TBW.

        :param processor:
        :return:
        """
        for step in self.enabled_steps:

            if isinstance(step.key, list) and isinstance(step.values, str):
                model_name_list = step.key[0]
                variable_name_lst = step.key[1]
                params_per_variable = step.key[2]
                split_list = []
                for i in range(len(params_per_variable)):
                    for j in range(len(params_per_variable[i])):
                        if i == 0 and j == 0:
                            split_list += [params_per_variable[0][0]]
                        else:
                            split_list += [split_list[-1] + params_per_variable[i][j]]

                data = np.loadtxt(step.values)
                data = data[:, 2:]

                if len(data[0, :]) != np.sum(np.sum(params_per_variable)):
                    raise ValueError

                for jj in range(len(data[:, 0])):
                    param = data[jj, :]
                    param_array_list = np.split(param, split_list)
                    param_array_list = param_array_list[:-1]

                    new_proc = deepcopy(processor)

                    k = 0
                    for i in range(len(model_name_list)):
                        if model_name_list[i] in ['geometry', 'material', 'environment', 'characteristics']:
                            class_str = model_name_list[i]
                            det_class = getattr(new_proc.detector, class_str)
                            for j in range(len(variable_name_lst[i])):
                                if len(param_array_list[k]) == 1:
                                    param_array_list[k] = param_array_list[k][0]
                                setattr(det_class, variable_name_lst[i][j], param_array_list[k])
                                k += 1
                        else:
                            fitted_pipeline_model = new_proc.pipeline.get_model(model_name_list[i])
                            for j in range(len(variable_name_lst[i])):
                                if len(param_array_list[k]) == 1:
                                    param_array_list[k] = param_array_list[k][0]
                                fitted_pipeline_model.arguments[variable_name_lst[i][j]] = param_array_list[k]
                                k += 1

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
        if self.parametric_mode == 'embedded':
            configs = self._embedded(processor)

        elif self.parametric_mode == 'sequential':
            configs = self._sequential(processor)

        elif self.parametric_mode == 'image_generator':
            configs = self._image_generator(processor)

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
