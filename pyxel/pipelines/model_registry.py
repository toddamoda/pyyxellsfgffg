"""TBW."""

import esapy_config as om
from pyxel.pipelines.processor import Processor
from pyxel.pipelines.model_group import ModelFunction


class registry:  # noqa: N801
    """TBW."""

    @staticmethod
    def get_group(detector, group=None):
        """TBW.

        :param detector:
        :param group:
        :return:
        """
        result = []
        for item in om.functions.values():
            item_detector = item.metadata.get('detector', '')
            if item_detector and detector not in item_detector:
                continue
            if group and item.metadata['group'] != group:
                continue
            result.append(item)
        return result

    @staticmethod
    def import_models(processor: Processor, name: str = None):
        """TBW.

        :param processor:
        :param name: group or model name
        """
        items = registry.get_group(processor.pipeline.name)
        for item in items:
            if not name or name == item.name or name == item.metadata.get('group', None):
                try:
                    import_model(processor, item)
                except Exception as exc:
                    print('Cannot import: %r', item)
                    print(exc)

    @staticmethod
    def decorator(*args, **kwargs):
        """TBW."""
        import pyxel
        return pyxel.register(*args, **kwargs)


def import_model(processor, model_def):
    """Dynamically import a model definition.

    :param processor:
    :param model_def:
    """
    if isinstance(model_def, om.FunctionDef):
        # model_def = dict(model_def)  # make copy
        group = model_def.metadata.get('group', None)
        if group in processor.pipeline.model_groups:
            model_group = processor.pipeline.model_groups[group]
            model = ModelFunction(name=model_def.name,
                                  func=model_def.func,
                                  arguments=model_def.arguments,
                                  enabled=model_def.enabled)
            model_group.models.append(model)
