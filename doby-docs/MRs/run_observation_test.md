# 🧪 Observation Mode -- Invalid Parameter Validation Test

**Filename:** `run_observation_test.py`
**Purpose:** Manual test script to verify that **invalid
`parameters.key`** in Observation mode triggers the improved error
message with a clear note pointing out the non-existing parameter.

------------------------------------------------------------------------

## 🔍 Description

This script creates a fake `Processor` and intentionally passes an
invalid parameter key to an `Observation`. It checks that the error
raised by `validate_steps` is not just the default *"missing parameter"*
but the **new improved message** that highlights the invalid part of the
key.

------------------------------------------------------------------------

## 📜 Script: `run_observation_test.py`

``` python
from pyxel.observation.observation import Observation
from pyxel.observation.types import ParameterValues, ParameterType
from pyxel.pipelines import Processor
from pyxel.readout import Readout


class FakeProcessor(Processor):
    def __init__(self):
        from pyxel.detectors import Detector
        from pyxel.pipelines import Pipeline

        # Minimal dummy setup
        detector = Detector()
        pipeline = Pipeline()
        super().__init__(detector, pipeline)

    def has(self, key: str) -> bool:
        # Always pretend the key is missing so validation is triggered
        return False

    def get(self, key: str):
        return None


# Intentionally invalid parameter key for testing
parameters = [
    ParameterValues(
        key="cfg.pipeline.charge_generation.exponential_qe.arguments.x_epi",  # <- invalid path
        values=[0.5],
        type=ParameterType.Simple,
        enabled=True,
    )
]

# Observation with invalid parameter
obs = Observation(
    parameters=parameters,
    readout=Readout(),
    mode="product",
)

processor = FakeProcessor()

# Run validation – should raise improved KeyError for invalid parameter
try:
    obs.validate_steps(processor)
except KeyError as e:
    print("✅ Custom error triggered:")
    print(e)
    raise
```

------------------------------------------------------------------------

## ✅ Expected Output

``` text
KeyError: "Missing parameter: 'cfg.pipeline.charge_generation.exponential_qe.arguments.x_epi'
                                                                            ^^^^^
                                                                            Non-existing parameter"
```

------------------------------------------------------------------------

## 📁 How to Run

From the project root:

``` bash
python tests/manual/run_observation_test.py
```
