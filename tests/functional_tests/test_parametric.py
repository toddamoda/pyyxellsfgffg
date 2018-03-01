import pytest


from pathlib import Path
# import typing as t
import numpy as np
import pytest
from astropy.io import fits

# from pyxel.pipelines.processor import Processor
# from pyxel.pipelines.ccd_pipeline import CCDDetectionPipeline
# from pyxel.pipelines.cmos_pipeline import CMOSDetectionPipeline
# from pyxel.detectors.ccd import CCD
from pyxel.io.yaml_processor import load_config

expected_single = [
    (0, [('level', 100), ('initial_energy', 100.0)])
]

expected_sequential = [
    (0, [('level', 10), ('initial_energy', 100.0)]),
    (1, [('level', 20), ('initial_energy', 100.0)]),
    (2, [('level', 30), ('initial_energy', 100.0)]),
    (3, [('level', 100), ('initial_energy', 100)]),
    (4, [('level', 100), ('initial_energy', 200)]),
    (5, [('level', 100), ('initial_energy', 300)])
]

expected_embedded = [
    (0, [('level', 10), ('initial_energy', 100)]),
    (1, [('level', 10), ('initial_energy', 200)]),
    (2, [('level', 10), ('initial_energy', 300)]),
    (3, [('level', 20), ('initial_energy', 100)]),
    (4, [('level', 20), ('initial_energy', 200)]),
    (5, [('level', 20), ('initial_energy', 300)]),
    (6, [('level', 30), ('initial_energy', 100)]),
    (7, [('level', 30), ('initial_energy', 200)]),
    (8, [('level', 30), ('initial_energy', 300)])
]


@pytest.mark.parametrize("mode, expected", [
    ('single', expected_single),
    ('sequential', expected_sequential),
    ('embedded', expected_embedded),
])
def test_pipeline_parametric(mode, expected):
    input_filename = 'tests/data/pipeline_parametric.yaml'
    cfg = load_config(Path(input_filename))
    parametric = cfg.pop('parametric')
    parametric.mode = mode
    processor = cfg[next(iter(cfg))]  # type: pyxel.pipelines.processor.Processor
    result = parametric.debug(processor)

    assert result == expected


# test_pipeline_parametric('single', expected_single)
# test_pipeline_parametric('sequential', expected_sequential)
# test_pipeline_parametric('embedded', expected_embedded)
