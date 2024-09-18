#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import logging
from typing import Any

from pyxel.observation import Observation
from pyxel.observation.deprecated import _processors_it
from pyxel.pipelines import Processor
from pyxel.pipelines.processor import _get_obj_att

expected_sequential = [
    (0, [("level", 10), ("initial_energy", 100)]),
    (1, [("level", 20), ("initial_energy", 100)]),
    (2, [("level", 30), ("initial_energy", 100)]),
    (3, [("level", 100), ("initial_energy", 100)]),
    (4, [("level", 100), ("initial_energy", 200)]),
    (5, [("level", 100), ("initial_energy", 300)]),
]

expected_product = [
    (0, [("level", 10), ("initial_energy", 100)]),
    (1, [("level", 10), ("initial_energy", 200)]),
    (2, [("level", 10), ("initial_energy", 300)]),
    (3, [("level", 20), ("initial_energy", 100)]),
    (4, [("level", 20), ("initial_energy", 200)]),
    (5, [("level", 20), ("initial_energy", 300)]),
    (6, [("level", 30), ("initial_energy", 100)]),
    (7, [("level", 30), ("initial_energy", 200)]),
    (8, [("level", 30), ("initial_energy", 300)]),
]


def get_value(obj: Any, key: str) -> Any:
    """Retrieve the attribute value of the object given the attribute dot formatted key chain.

    Example::

        >>> obj = {"processor": {"pipeline": {"models": [1, 2, 3]}}}
        >>> om.get_value(obj, "processor.pipeline.models")
        [1, 2, 3]

    The above example works as well for a user-defined object with a attribute
    objects, i.e. configuration object model.
    """
    obj, att = _get_obj_att(obj, key)

    if isinstance(obj, dict) and att in obj:
        value = obj[att]
    else:
        value = getattr(obj, att)

    return value


def debug_parameters(observation: Observation, processor: Processor) -> list:
    """List the parameters using processor parameters in processor generator."""
    result = []
    processor_generator = _processors_it(observation, processor=processor)
    for i, (proc, _, _) in enumerate(processor_generator):
        values = []
        for step in observation.enabled_steps:
            _, att = _get_obj_att(proc, step.key)
            value = get_value(proc, step.key)
            values.append((att, value))
        logging.debug("%d: %r", i, values)
        result.append((i, values))
    return result
