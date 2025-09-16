from pyxel.observation.observation import Observation
from pyxel.observation import ParameterValues
from pyxel.pipelines.processor import Processor
import yaml


with open("invalid_parameter_test.yaml", "r") as f:
    config = yaml.safe_load(f)


raw_parameters = config["observation"]["parameters"]
parameters = [ParameterValues(**param) for param in raw_parameters]


class FakeDetector:
    pass

fake_pipeline = {}


processor = Processor(
    detector=FakeDetector(),
    pipeline=fake_pipeline,
)


processor.steps = {
    "cfg.pipeline.charge_generation.exponential_qe.arguments.energy_levels": lambda: None
}

processor.has = lambda key: key in processor.steps
processor.get = lambda key: True 


obs = Observation(
    parameters=parameters,
    mode="product",
)


obs.validate_steps(processor)
