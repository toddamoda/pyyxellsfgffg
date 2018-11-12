"""TBW."""
import itertools
import typing as t
from copy import deepcopy
import esapy_config as om


class StepValues:
    """TBW."""

    def __init__(self, key, values,
                 enabled=True, current=None,
                 model_names=None, variables=None, params_per_variable=None):
        """TBW.

        :param key:
        :param values:
        :param enabled:
        :param current:
        """
        # TODO: should the values be evaluated?
        self.key = key  # unique identifier to the step. example: detector.geometry.row
        self.values = values  # t.List[float|int]
        self.enabled = enabled  # bool
        self.current = current

        self.model_names = model_names
        self.variables = variables
        self.params_per_variable = params_per_variable

    # def copy(self):
    #     """TBW."""
    #     kwargs = {key: type(value)(value) for key, value in self.__getstate__().items()}
    #     return StepValues(**kwargs)

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
        values = om.eval_range(self.values)
        return len(values)

    def __iter__(self):
        """TBW."""
        values = om.eval_range(self.values)
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

    # def copy(self):
    #     """TBW."""
    #     return Configuration(self.parametric_mode, [step.copy() for step in self.steps])

    def get_state_json(self):
        """TBW."""
        return om.get_state_dict(self)

    def __getstate__(self):
        """TBW."""
        return {'mode': self.parametric_mode, 'steps': self.steps}

    @property
    def enabled_steps(self):
        """TBW."""
        return [step for step in self.steps if step.enabled]

    def _image_generator(self, processor):
        """TBW.

        :param processor:
        :return:
        """
        # todo generate keys from
        # todo update all arg
        # todo generate new processors

        # for step in self.enabled_steps:
        #
        #     model_names = step.model_names
        #     variables = step.variables
        #     params_per_variable = step.params_per_variable
        #
        #     key = step.key
        #     todo read calibration_champion.out file
        #
        #     for value in step:
        #
        #         step.current = value
        #
        #
        #         new_proc = deepcopy(processor)
        #         new_proc.set(key, value)
        #         yield new_proc
        pass

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
                _, att = om.get_obj_att(config, step.key)
                value = om.get_value(config, step.key)
                values.append((att, value))
            print('%d: %r' % (i, values))
            result.append((i, values))
        return result


class Configuration:
    """TBW."""

    def __init__(self, mode,
                 parametric_analysis=None,
                 calibration=None
                 ) -> None:
        """TBW.

        :param mode:
        :param parametric_analysis:
        :param calibration:
        """
        self.mode = mode
        self.parametric_analysis = parametric_analysis
        self.calibration = calibration

    def get_state_json(self):
        """TBW."""
        return om.get_state_dict(self)
