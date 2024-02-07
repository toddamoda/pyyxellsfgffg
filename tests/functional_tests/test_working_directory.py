#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import os
import shutil
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import numpy as np
import pytest
from astropy.io import fits
from freezegun import freeze_time

import pyxel
from pyxel.util import complete_path


@contextmanager
def chdir(folder: Path):
    current_folder = Path().resolve()

    try:
        os.chdir(folder)
        yield
    finally:
        os.chdir(current_folder)


@pytest.mark.parametrize(
    "work_dir",
    [
        None,  # current working directory (no working_directory)
        "work_dir_relative_to_cur_dir",
        "~/work_dir_user_dir",
    ],
)
def test_working_directory(work_dir):
    date_2023_12_18_08_20 = datetime(
        year=2023,
        month=12,
        day=18,
        hour=8,
        minute=20,
    )
    config_file = "data/simple_exposure_for_work_dir.yaml"
    with chdir(Path(__file__).parent):
        try:
            config = pyxel.load(config_file)

            # Save 2d images
            data_2d = np.array([[1, 2], [3, 4]], dtype=np.uint16)
            image_file = config.pipeline.photon_collection.models[0].arguments[
                "image_file"
            ]
            # This is where the loader function will look for the image
            image_file = Path(complete_path(image_file, work_dir)).expanduser()
            assert not image_file.exists()

            input_dir = Path(image_file).parent.expanduser()
            assert not input_dir.exists()

            try:
                input_dir.mkdir(parents=True, exist_ok=True)
                assert input_dir.exists()

                try:
                    fits.writeto(image_file, data=data_2d, overwrite=True)
                    assert image_file.exists()

                    output_folder = config.exposure.outputs.output_folder

                    try:
                        # This is where the output files will be located
                        output_dir = complete_path(
                            filename=output_folder, working_dir=work_dir
                        ).expanduser()
                        assert not output_dir.exists()

                        config.exposure.working_directory = work_dir
                        with freeze_time(date_2023_12_18_08_20):
                            pyxel.run_mode(
                                mode=config.exposure,
                                detector=config.detector,
                                pipeline=config.pipeline,
                            )

                        # check that the folders exist
                        assert config.exposure.outputs.current_output_folder.exists()
                        assert output_dir.exists()

                    finally:
                        # remove output folder
                        shutil.rmtree(output_dir, ignore_errors=True)

                finally:
                    # remove input folder and image file
                    image_file.unlink(missing_ok=True)

            finally:
                input_dir.rmdir()

        finally:
            if work_dir:
                shutil.rmtree(Path(work_dir).expanduser(), ignore_errors=True)
