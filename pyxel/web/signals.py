# import typing as t

from esapy_dispatcher import DispatcherBlocking
from esapy_dispatcher.dispatcher_meta import from_ref


HK_SIGNAL = 'HK_SIGNAL'
DATA_READY = 'DATA_READY'
PAUSE = 'PAUSE'
RESUME = 'RESUME'
STOP = 'STOP'
RUN_APPLICATION = 'RUN-APPLICATION'
RUN_PIPELINE = 'RUN-PIPELINE'
SET_SETTING = 'SET-SETTING'
GET_SETTING = 'GET-SETTING'
PROGRESS = 'PROGRESS'
SET_SEQUENCE = 'SET-SEQUENCE'


class DispatcherBlockingAutoRemoveDeadEndPoints(DispatcherBlocking):

    def _find_endpoints(self, sender='', signal=''):
        endpoints = super()._find_endpoints(sender=sender, signal=signal)
        self._remove_dead_endpoints(endpoints, sender, signal)
        return super()._find_endpoints(sender=sender, signal=signal)

    def _remove_dead_endpoints(self, endpoints, sender='', signal=''):
        # automatically remove and dead end points
        if not endpoints:
            return
        dead_endpoints = []
        for endpoint_ref in endpoints:
            try:
                obj_ref = from_ref(endpoint_ref)  # type: t.Any
                if obj_ref is None:
                    dead_endpoints.append(endpoint_ref)
            except ReferenceError:
                dead_endpoints.append(endpoint_ref)

        for dead_endpoint in dead_endpoints:
            self._log.warning('Removing end-point: sender:%r, signal:%r, dead_endpoint: %r',
                              sender, signal, dead_endpoint)
            endpoints.remove(dead_endpoint)


dispatcher = DispatcherBlockingAutoRemoveDeadEndPoints()
# send_to_influxdb = dispatcher.emit(sender='*', signal=HK_SIGNAL)
progress = dispatcher.emit(sender='*', signal=PROGRESS)


class SequencerState:
    """ The state of the sequencer. """

    error = -1
    idle = 0
    running = 1
    pause = 2
    completed = 3
    aborted = 4

    @staticmethod
    def to_string(state):
        state_map = {
            SequencerState.error: 'error',
            SequencerState.idle: 'idle',
            SequencerState.running: 'running',
            SequencerState.pause: 'paused',
            SequencerState.completed: 'completed',
            SequencerState.aborted: 'aborted'
        }
        return state_map[state]
