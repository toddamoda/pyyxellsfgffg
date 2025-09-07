from pyxel.observation.observation import Observation
from pyxel.pipelines.processor import Processor
import yaml

# Load your YAML file
with open("invalid_parameter_test.yaml", "r") as f:
    config = yaml.safe_load(f)

parameters = config["observation"]["parameters"]


class FakeProcessor(Processor):
    def __init__(self):
        super().__init__(steps=[])
        self.steps["cfg.pipeline.charge_generation.exponential_qe.arguments.energy_levels"] = lambda: None

    def has(self, key):
        return key in self.steps

    def get(self, key):
        return True  


processor = FakeProcessor()

obs = Observation(
    parameters=parameters,
    mode="product",
)

obs.validate_steps(processor)
