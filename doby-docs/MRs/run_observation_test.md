# 🧪 Observation Mode – Invalid Parameter Test

**Filename:** `run_observation_test.py`  
**Location:** `pyxel/` root folder or inside `tests/manual/` (as appropriate)  
**Purpose:** Manual test script for verifying the improved KeyError output when invalid `parameters.key` is used in Observation mode.

---

## 🔍 Description

This script simulates a broken pipeline step reference by intentionally providing an invalid key in the Observation parameters.

### Why?

To verify that the improved error message logic in `observation.py` correctly identifies and highlights the broken part of the key path, giving a user-friendly, debuggable error.

---

## 📜 Script: `run_observation_test.py`

```python
from pyxel.observation.observation import Observation
from pyxel.observation.types import ParameterValues, ParameterType
from pyxel.pipelines import Processor
from pyxel.readout import Readout


class FakeProcessor(Processor):
    def __init__(self):
        from pyxel.detectors import Detector
        from pyxel.pipelines import Pipeline

        # Create an empty Processor with minimal Detector and Pipeline
        detector = Detector()
        pipeline = Pipeline()
        super().__init__(detector, pipeline)

    def has(self, key: str) -> bool:
        return False  # Simulate missing parameter key

    def get(self, key: str):
        return None


parameters = [
    ParameterValues(
        key="cfg.pipeline.charge_generation.exponential_qe.arguments.x_epi",  # Invalid key
        values=[0.5],
        type=ParameterType.Simple,
        enabled=True,
    )
]

obs = Observation(
    parameters=parameters,
    readout=Readout(),
    mode="product",
)

processor = FakeProcessor()

# This should raise your custom improved KeyError
obs.validate_steps(processor)
```

---

## ✅ Expected Output

```text
KeyError: "Missing parameter: 'cfg.pipeline.charge_generation.exponential_qe.arguments.x_epi'
                                                                            ^^^^^
                                                                            Non-existing parameter"
```

---

## 📁 How to Use

Run the script from the project root:

```bash
python run_observation_test.py
```

---

## 🧡 Notes

You can include this in your `MRs/` folder or reference it in your merge request to help reviewers quickly understand the context and test your changes manually.
