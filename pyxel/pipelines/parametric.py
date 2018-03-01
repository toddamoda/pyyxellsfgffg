"""TBW."""
import itertools
import typing as t

from pyxel import util

class StepValues:
    """TBW."""

    def __init__(self, key, values, enabled=True):
        """TBW.

        :param key:
        :param values:
        :param enabled:
        """
        self.key = key  # unique identifier to the step. example: detector.geometry.row
        self.values = values  # t.List[float|int]
        self.enabled = enabled  # bool

    def __iter__(self):
        """TBW."""
        for value in self.values:
            yield value

    # def apply_value(self, processor, value):
    #     """TBW.
    #
    #     :param processor:
    #     :param value:
    #     :return:
    #     """
    #     if value:
    #         if isinstance(value, list):
    #             for i, val in enumerate(value):
    #                 if val:
    #                     value[i] = util.eval_entry(val)
    #         else:
    #             value = util.eval_entry(value)
    #
    #     obj, att = util.get_obj_att(processor, self.key)
    #
    #     if isinstance(obj, dict) and att in obj:
    #         obj[att] = value
    #     else:
    #         setattr(obj, att, value)


class ParametricConfig:
    """TBW."""

    def __init__(self, mode, steps: t.List[StepValues]) -> None:
        """TBW.

        :param mode:
        :param steps:
        """
        self.steps = steps
        self.mode = mode

    @property
    def enabled_steps(self):
        """TBW."""
        return [step for step in self.steps if step.enabled]

    def _sequential(self, processor):
        """TBW.

        :param processor:
        :return:
        """
        # configs = []
        #
        for step in self.enabled_steps:
            key = step.key
            for value in step:
                new_proc = util.copy_processor(processor)
                new_proc.set(key, value)
                yield new_proc
                # # step.apply_value(proc, value)
                # configs.append(proc)
        #
        # return configs

    def _embedded(self, processor, level=0, configs=None):
        """TBW.

        :param processor:
        :param level:
        :param sequence:
        :return:
        """
        all_steps = self.enabled_steps
        keys = [step.key for step in self.enabled_steps]
        for params in itertools.product(*all_steps):
            new_proc = util.copy_processor(processor)
            for key, value in zip(keys, params):
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
                configs.append(util.copy_processor(processor))

        return configs

    def collect(self, processor):
        """TBW."""
        if self.mode == 'embedded':
            configs = self._embedded(util.copy_processor(processor))

        elif self.mode == 'sequential':
            configs = self._sequential(util.copy_processor(processor))

        elif self.mode == 'single':
            configs = [util.copy_processor(processor)]

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
                _, att = util.get_obj_att(config, step.key)
                value = util.get_value(config, step.key)
                values.append((att, value))
            print('%d: %r' % (i, values))
            result.append((i, values))
        return result
