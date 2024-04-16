#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from pyxel.calibration.fitting_datatree import ModelFittingDataTree
from pyxel.detectors import CCD, CCDGeometry, Characteristics, Environment
from pyxel.pipelines import DetectionPipeline, ModelFunction, Processor


def test_model_fitting_datatree():

    detector = CCD(
        geometry=CCDGeometry(row=835, col=1),
        environment=Environment(),
        characteristics=Characteristics(),
    )
    pipeline = DetectionPipeline(charge_transfer=[ModelFunction()])
    processor = Processor(detector=detector, pipeline=pipeline)

    _ = ModelFittingDataTree(processor=processor)
