"""TBW."""

import logging
from pathlib import Path
# import argparse
# import typing as t  # noqa: F401

# import tornado.web

import esapy_web.webapp2.modules.guiconfig.guiconfig_serializer as serializer
from esapy_dispatcher import dispatcher
from esapy_web.webapp2 import webapp
from esapy_web.webapp2.modules import guiconfig
from esapy_web.webapp2.modules import sequencer
from esapy_web.webapp2.modules import dispatch

# import pyxel
# import pyxel.pipelines.processor
from pyxel.pipelines.model_registry import registry         # TODO get rid of pyxel dependency


from pyxel.web2 import controller


class PipelinePageHandler(guiconfig.IndexPageHandler):
    """The index.html HTML generation handler."""

    def get(self, name):
        """TBW."""
        self.application.settings['gui_controller'].load_template(name)
        super(PipelinePageHandler, self).get()

    @property
    def detector(self):
        """TBW."""
        config = self.application.settings['gui_controller'].config
        if config:
            value = config.pipeline.name
        return value

    @property
    def pipelines(self):
        """TBW."""
        values = self.application.settings['gui_controller'].get_pipeline_names()
        return values

    @property
    def model_groups(self):
        """TBW."""
        values = self.application.settings['gui_controller'].model_groups
        return values

    def groups(self):
        """Dynamically create the object model GUI schema.

        This method is referenced in control.html template file.

        :return:
        """
        sections_detector = []
        sections_model = []
        cfg = {
            'gui': [
                {
                    'label': 'Detector Attributes',
                    'section': sections_detector,
                },
                {
                    'label': 'Models Settings',
                    'section': sections_model,
                }
            ]
        }
        # serializer = serializer.Serializer
        processor = self.application.settings['gui_controller'].config
        if processor:
            items = processor.detector.__getstate__().items()
            for key, value in items:
                sections = serializer.Serializer.create_section_from_object(value, 'detector.' + key)
                sections_detector.extend(sections)

            pipeline = processor.pipeline
            for group in pipeline.model_group_names:
                items = registry.get_group(pipeline.name, group)             # TODO get rid of pyxel dependency
                for item in items:
                    prefix = 'pipeline.' + group + '.' + item.name + '.arguments'
                    gui_def = serializer.Serializer.create_section_from_func_def(item, prefix)
                    sections_model.append(gui_def)

        for group in cfg['gui']:
            for section in group['section']:
                for item in section['items']:
                    item['button_label'] = 'SET'

        import json
        file_name = 'gui_pyxel.json'
        file_path = Path('/tmp/guiconfig', file_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open('w') as fp:
            json.dump(cfg, fp, indent=4)

        return cfg['gui']


def run_web_server(port=9999, js9_dir='../pyxel_js9', data_dir='../data'):
    """TBW.

    :param port:
    :param address_viewer:
    :param js9_dir:
    :param data_dir:
    """
    ctrl = controller.Controller(dispatcher)
    web_dir = Path(__file__).parent.joinpath('static')
    # guiconfig.settings['gui_controller'] = ctrl
    modules = webapp.Modules(dispatcher=dispatcher,
                             modules=[dispatch, guiconfig, sequencer],
                             static_path=('/pyxel/(.*)', web_dir),
                             index_template_file=web_dir.joinpath('main.html'))
    app_handlers = [
        ('/pipeline/(.*)', PipelinePageHandler, {}, None),
        # ('/pyxel/(.*)', webapp.MultiStaticPage, {}, None),
        # ('/js9/(.*)', tornado.web.StaticFileHandler, {'path': js9_dir}, None),      # TODO do we need this?
        # ('/data/(.*)', tornado.web.StaticFileHandler, {'path': data_dir}, 'data'),  # TODO do we need this?
    ]
    modules.settings['gui_controller'] = ctrl
    modules.settings['template_paths'].append(web_dir)
    modules.handlers.extend(app_handlers)

    api = webapp.WebApplication(modules.handlers, modules.settings)
    # thread = webapp.TornadoServer(api, ('0.0.0.0', port), additional_url='/pipeline/ccd')  # todo: added by David
    thread = webapp.TornadoServer(api, ('0.0.0.0', port))
    try:
        thread.run()
    except KeyboardInterrupt:
        logging.info("Exiting web server")
    finally:
        thread.stop()


# def run_web_server_org(port=9999, js9_dir=None, data_dir=None):
#     """TBW.
#
#     :param port:
#     :param js9_dir:
#     :param data_dir:
#     """
#     ctrl = controller.Controller()
#
#     handlers = [
#         ('/pipeline/(.*)', PipelinePageHandler, {}, None),
#         ('/pyxel/(.*)', webapp.MultiStaticPage, {}, None),
#         ('/js9/(.*)', tornado.web.StaticFileHandler, {'path': js9_dir}, None),
#         ('/data/(.*)', tornado.web.StaticFileHandler, {'path': data_dir}, 'data'),
#         # Rule(matcher, target, target_kwargs, name)
#     ]   # type: t.List[t.Tuple[str, t.Any, t.Dict[str, t.Any], str]]
#
#     settings = {
#         'web_dir': str(Path(__file__).parent.joinpath('static')),
#         'index_template': 'main.html',
#     }
#     api = webapp.WebApplication(ctrl, dispatcher, handlers, settings)
#
#     def set_data_path(path, *args):
#         web_uri = path.split('data')[0] + 'data'
#         api.wildcard_router.named_rules['data'].target_kwargs['path'] = web_uri
#
#     dispatcher.connect(sender='api', signal=controller.OUTPUT_DATA_DIR, callback=set_data_path)
#     thread = webapp.TornadoServer(api, ('0.0.0.0', port))
#     try:
#         thread.run()
#     except KeyboardInterrupt:
#         logging.info("Exiting web server")
#     finally:
#         thread.stop()


# def main():
#     """TBW."""
#     parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
#                                      description=__doc__)
#
#     parser.add_argument('-p', '--port', default=9999, type=int,
#                         help='The port to run the web server on')
#
#     parser.add_argument('-d', '--data-dir', default='../data',
#                         help='Data directory')
#
#     parser.add_argument('-j', '--js9-dir', default='../pyxel_js9',
#                         help='JS9 directory')
#
#     parser.add_argument('-v', '--verbosity', action='count', default=0,
#                         help='Increase output verbosity')
#
#     parser.add_argument('--version', action='version',
#                         version='%(prog)s (version {version})'.format(version=pyxel.__version__))
#
#     opts = parser.parse_args()
#
#     # Set logger
#     log_level = [logging.ERROR, logging.INFO, logging.DEBUG][min(opts.verbosity, 2)]
#     log_format = '%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(thread)d - %(message)s'
#     del logging.root.handlers[:]
#     logging.basicConfig(level=log_level, format=log_format)
#
#     run_web_server(opts.port, opts.js9_dir, opts.data_dir)
#
#
# if __name__ == '__main__':
#     main()
