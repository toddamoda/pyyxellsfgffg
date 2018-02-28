"""Parameterized sequencer that modifies a setting and runs the pipeline."""
import logging
import threading

from pyxel.web import signals
from pyxel.web import util


class Sequencer:
    """TBW."""

    def __init__(self, controller):
        """TBW.

        :param controller:
        :param steps:
        :param output_file:
        """
        self._log = logging.getLogger(__name__)
        self._controller = controller
        self._output_file = None
        # self._steps = steps  # type: t.List[dict]  # key[str], values[list], enabled[bool]
        self._current = None  # type: dict

        self._paused = False
        self._running = False
        self._th = None  # type: threading.Thread

        self._step = 0
        self._level = 0
        self._n_steps = 1
        self._run_mode = 'recurse'

        self._steps = [  # TODO: create a Step class
            {'key': '', 'values': [], 'enabled': False},
            {'key': '', 'values': [], 'enabled': False},
            {'key': '', 'values': [], 'enabled': False},
            {'key': '', 'values': [], 'enabled': False},
            {'key': '', 'values': [], 'enabled': False},
        ]

    def set_mode(self, mode):
        """Set the mode to run the sequencer in.

        :param mode: accepted values: recurse, linear, single

        """
        self._run_mode = mode

    def set_output_file(self, output_file):
        """TBW.

        :param output_file:
        """
        self._output_file = output_file

    def set_range(self, index, key, values, enabled):
        """TBW.

        :param index:
        :param key:
        :param values:
        :param enabled:
        """
        values = util.eval_range(values)
        self._steps[index]['key'] = key
        self._steps[index]['values'] = values
        self._steps[index]['enabled'] = enabled

    @property
    def enabled_steps(self):
        """TBW."""
        result = []
        for step in self._steps:
            if step['enabled']:
                result.append(step)
        return result

    def is_running(self) -> bool:
        """TBW."""
        return self._running

    def start(self):
        """TBW."""
        self._th = threading.Thread(target=self.run)
        self._th.start()

    def join(self):
        """TBW."""
        if self._th is not None:
            self._th.join()
        self._th = None

    def stop(self):
        """TBW."""
        self._paused = False  # abort any paused state as well.
        self._running = False

    def _run_step(self, step, val):
        # self._log.info('Step %d of %d', self._step, self._n_steps)
        signals.progress('state', {'value': 'running', 'state': 1})
        try:
            key = step['key']
            self._controller.set_setting(key, val)
            signals.progress('sequence_%d' % self._level, {'value': val, 'state': 1})
            # run_pipeline(self._controller.processor, self._output_file)
            signals.progress('sequence_%d' % self._level, {'value': val, 'state': 0})
        except Exception as exc:
            self._log.exception(exc)
            pass  # TODO: what to do?

    def _load_initial_state(self):
        for i, step in enumerate(self.enabled_steps):
            if len(step['values']):
                val_0 = step['values'][0]
                key = step['key']
                self._controller.set_setting(key, val_0)
                signals.progress('sequence_%d' % i, {'value': val_0, 'state': 1})

    def _single(self):
        """TBW."""
        try:
            util.run_pipeline(self._controller.processor, self._output_file, self._controller.address_viewer)
        except Exception as exc:
            self._log.exception(exc)
            pass  # TODO: what to do?

    def _loop(self):
        """Linear loop method."""
        for i, step in enumerate(self.enabled_steps):  # step = self.enabled_steps[i]
            if not self.is_running():
                break
            self._level = i
            self._current = step
            for val in step['values']:
                if not self.is_running():
                    break

                self._step += 1
                self._run_step(step, val)
                self._single()

    def _recurse(self, i=0):
        """Recursive loop method.

        .. warning:: this method is re-entrant
        """
        step = self.enabled_steps[i]
        self._level = i
        self._current = step
        for val in step['values']:
            # check if the loop is still running
            if not self.is_running():
                break

            self._step += 1
            self._run_step(step, val)
            if i+1 < len(self.enabled_steps):
                self._recurse(i+1)
                # check if user-defined exit handler was called
                if not self.is_running():
                    break
                self._level = i
                self._current = step  # reset back to this context's step
            else:
                self._single()

    def _calculate_total_steps(self):
        """Calculate the number of steps in a recursive loop.

        The following equation is implemented::

            total steps = L3*(1+L2*(1+L1*(1+L0)))

        Where,

            * L0 is the outer most loop count
            * L3 is the inner most loop.

        Of course, this loop has no depth limit, so L3 is actually LN in this
        case.
        """
        num_steps = 1
        if self._run_mode == 'recurse':
            for item in reversed(self.enabled_steps):
                num_steps = 1 + len(list(item)) * num_steps
            num_steps -= 1
        elif self._run_mode == 'linear':
            for item in reversed(self.enabled_steps):
                num_steps += len(list(item))
        self._n_steps = num_steps

    def run(self):
        """TBW."""
        self._running = True
        try:
            self._calculate_total_steps()
            if self._run_mode == 'recurse':
                # self._load_initial_state()
                self._recurse(0)
            elif self._run_mode == 'linear':
                # self._load_initial_state()
                self._loop()
            else:
                self._single()

            if self._running:
                signals.progress('state', {'value': 'completed', 'state': 0})
            else:
                signals.progress('state', {'value': 'aborted', 'state': 0})

        except Exception as exc:
            signals.progress('state', {'value': 'error', 'state': -1})
            self._log.exception(exc)

        finally:
            self._running = False
