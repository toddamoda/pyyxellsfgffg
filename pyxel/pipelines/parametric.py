"""TBW."""
import itertools
import typing as t

import esapy_config as om
# from pyxel.util import objmod as om


class StepValues:
    """TBW."""

    def __init__(self, key, values, enabled=True, current=None):
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

    def copy(self):
        """TBW."""
        kwargs = {key: type(value)(value) for key, value in self.__getstate__().items()}
        return StepValues(**kwargs)

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


class Configuration:
    """TBW."""

    def __init__(self, mode, steps: t.List[StepValues]) -> None:
        """TBW.

        :param mode:
        :param steps:
        """
        self.steps = steps
        self.mode = mode

    def copy(self):
        """TBW."""
        return Configuration([step.copy() for step in self.steps], self.mode)

    def get_state_json(self):
        """TBW."""
        return om.get_state_dict(self)

    def __getstate__(self):
        """TBW."""
        return {
            'steps': self.steps,
            'mode': self.mode
        }

    @property
    def enabled_steps(self):
        """TBW."""
        return [step for step in self.steps if step.enabled]

    def _sequential(self, processor):
        """TBW.

        :param processor:
        :return:
        """
        for step in self.enabled_steps:
            key = step.key
            for value in step:
                step.current = value
                new_proc = om.copy_processor(processor)
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
            new_proc = om.copy_processor(processor)
            for key, value in zip(keys, params):
                for step in all_steps:
                    if step.key == key:
                        step.current = value
                new_proc.set(key=key, value=value)
            yield new_proc

    def _embedded_org(self, processor, level=0, configs=None):
        """TBW.

        :param processor:
        :param level:
        :param sequence:
        :return:
        """
        if configs is None:
            configs = []

        step = self.enabled_steps[level]
        key = step.key
        for value in step:
            processor.set(key, value)
            if level+1 < len(self.enabled_steps):
                self._embedded(processor, level+1, configs)
            else:
                configs.append(om.copy_processor(processor))

        return configs

    def collect(self, processor):
        """TBW."""
        if self.mode == 'embedded':
            configs = self._embedded(om.copy_processor(processor))

        elif self.mode == 'sequential':
            configs = self._sequential(om.copy_processor(processor))

        elif self.mode == 'single':
            # configs = [om.copy_processor(processor)]
            configs = [processor]

        elif self.mode == 'calibration':
            # configs = [om.copy_processor(processor)]
            configs = [processor]
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
