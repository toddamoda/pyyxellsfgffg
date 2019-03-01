"""TBW."""
import esapy_config.io as io


def pyxel_yaml_loader():
    """TBW."""
    from pyxel.parametric.parametric import Configuration
    from pyxel.parametric.parametric import ParametricAnalysis
    from pyxel.parametric.parameter_values import ParameterValues
    
    try:
        from pyxel.calibration.calibration import Calibration
        from pyxel.calibration.calibration import Algorithm
        WITH_CALIBRATION = True
    except ImportError:
        # No calibration
        WITH_CALIBRATION = False
    
    from pyxel.pipelines.model_function import ModelFunction
    from pyxel.pipelines.model_group import ModelGroup
    from pyxel.util import Outputs

    io.ObjectModelLoader.add_class_ref(['detector', 'class'])
    io.ObjectModelLoader.add_class_ref(['detector', None, 'class'])

    io.ObjectModelLoader.add_class_ref(['pipeline', 'class'])
    io.ObjectModelLoader.add_class(ModelGroup, ['pipeline', None])
    io.ObjectModelLoader.add_class(ModelFunction, ['pipeline', None, None])

    io.ObjectModelLoader.add_class(Configuration, ['simulation'])

    io.ObjectModelLoader.add_class(Outputs, ['simulation', 'outputs'])

    io.ObjectModelLoader.add_class(ParametricAnalysis, ['simulation', 'parametric'])
    io.ObjectModelLoader.add_class(ParameterValues, ['simulation', 'parametric', 'parameters'], is_list=True)

    if WITH_CALIBRATION:
        io.ObjectModelLoader.add_class(Calibration, ['simulation', 'calibration'])
        io.ObjectModelLoader.add_class(Algorithm, ['simulation', 'calibration', 'algorithm'])
    
    io.ObjectModelLoader.add_class(ModelFunction, ['simulation', 'calibration', 'fitness_function'])
    io.ObjectModelLoader.add_class(ParameterValues, ['simulation', 'calibration', 'parameters'], is_list=True)


pyxel_yaml_loader()
