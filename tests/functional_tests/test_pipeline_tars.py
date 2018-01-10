from pathlib import Path

from pyxel.detectors.ccd import CCDDetector
from pyxel.pipelines import ccd_pipeline
from pyxel.pipelines.yaml_processor import load_config
from pyxel.pipelines.yaml_processor import save_signal


def test_pipeline_tars():

    # Step 1: Get the pipeline configuration
    config_path = Path(__file__).parent.joinpath('pipeline_tars.yaml')
    cfg = load_config(str(config_path))

    # Step 2: Run the pipeline
    result = ccd_pipeline.run_pipeline(cfg)         # type: CCDDetector
    print('Pipeline completed.')

    # Step 3: Save the result(s) in FITS, ASCII, Jupyter Notebook(s), ...
    save_signal(ccd=result, output_filename='result.fits')
