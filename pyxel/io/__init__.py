"""TBW."""
import esapy_config.io as io
load = io.load


def pyxel_yaml_loader():
    """TBW."""
    from pyxel.parametric.parametric import Configuration
    from pyxel.parametric.parametric import ParametricAnalysis
    from pyxel.parametric.parameter_values import ParameterValues
    from pyxel.pipelines.model_function import ModelFunction
    from pyxel.pipelines.model_group import ModelGroup
    from pyxel.util import Outputs

    try:
        from pyxel.calibration.calibration import Calibration
        from pyxel.calibration.calibration import Algorithm
        io.ObjectModelLoader.add_class(Calibration, ['simulation', 'calibration'])
        io.ObjectModelLoader.add_class(Algorithm, ['simulation', 'calibration', 'algorithm'])
        io.ObjectModelLoader.add_class(ModelFunction, ['simulation', 'calibration', 'fitness_function'])
        io.ObjectModelLoader.add_class(ParameterValues, ['simulation', 'calibration', 'parameters'], is_list=True)
        # WITH_CALIBRATION = True  # noqa: N806
    except ImportError:
        # WITH_CALIBRATION = False  # noqa: N806
        pass

    from pyxel.detectors import CCD, CMOS, Detector
    from pyxel.detectors import Geometry, Characteristics, Material, Environment
    from pyxel.detectors.ccd import CCDGeometry, CCDCharacteristics
    from pyxel.detectors.cmos import CMOSGeometry, CMOSCharacteristics

    from pyxel.pipelines.pipeline import DetectionPipeline

    io.ObjectModelLoader.add_class(CCD, ['ccd_detector'])  # pyxel.detectors.ccd.CCD
    io.ObjectModelLoader.add_class(CMOS, ['cmos_detector'])
    io.ObjectModelLoader.add_class(Detector, ['detector'])

    io.ObjectModelLoader.add_class(CCDGeometry, ['ccd_detector', 'geometry'])
    io.ObjectModelLoader.add_class(CMOSGeometry, ['cmos_detector', 'geometry'])
    io.ObjectModelLoader.add_class(Geometry, ['detector', 'geometry'])

    io.ObjectModelLoader.add_class(CCDCharacteristics, ['ccd_detector', 'characteristics'])
    io.ObjectModelLoader.add_class(CMOSCharacteristics, ['cmos_detector', 'characteristics'])
    io.ObjectModelLoader.add_class(Characteristics, ['detector', 'characteristics'])

    io.ObjectModelLoader.add_class(Material, [None, 'material'])
    io.ObjectModelLoader.add_class(Environment, [None, 'environment'])

    io.ObjectModelLoader.add_class(DetectionPipeline, ['pipeline'])

    io.ObjectModelLoader.add_class(ModelGroup, ['pipeline', None])
    io.ObjectModelLoader.add_class(ModelFunction, ['pipeline', None, None])

    io.ObjectModelLoader.add_class(Configuration, ['simulation'])

    io.ObjectModelLoader.add_class(Outputs, ['simulation', 'outputs'])

    io.ObjectModelLoader.add_class(ParametricAnalysis, ['simulation', 'parametric'])
    io.ObjectModelLoader.add_class(ParameterValues, ['simulation', 'parametric', 'parameters'], is_list=True)


pyxel_yaml_loader()
