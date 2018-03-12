from pyxel import MetaModel
from pyxel import registry
from pyxel.detectors.detector import Detector


class MyClassModel(metaclass=MetaModel,
                   model_name='my_class_model',
                   model_group='charge_generation'):

    def __call__(self, detector: Detector, level: int, noise: float=2.0):
        setattr(detector, 'level', level)
        setattr(detector, 'noise', noise)
        return detector


class MyOtherClassModel(metaclass=MetaModel,
                        model_name='my_other_class_model',
                        model_group='charge_generation'):

    def __call__(self, detector: Detector, std: float=2.0):
        setattr(detector, 'std', std)
        return detector


def my_function_model(detector: Detector, level, noise: float=2.0):
    # set a new attribute so it can be checked later
    setattr(detector, 'level', level)
    setattr(detector, 'noise', noise)
    return detector


registry.register(my_function_model, model_group='charge_generation')
