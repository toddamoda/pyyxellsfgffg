"""TBW."""

import json
import threading
import os
import logging

import tornado
import tornado.websocket
import tornado.httpserver
import tornado.web

from pyxel.web import signals

WEB_SOCKETS = []
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))


def announce_progress(idn: str, fields: dict):
    """TBW.

    :param idn:
    :param fields:
    :return:
    """
    msg = {
        'type': 'progress',
        'id': idn,
        'fields': fields,
    }
    WebSocketHandler.announce(msg)


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """The ws: web-socket handler."""

    def open(self):
        """TBW."""
        WEB_SOCKETS.append(self)

    def on_close(self):
        """TBW."""
        WEB_SOCKETS.remove(self)

    @staticmethod
    def announce(object_dict):
        """TBW.

        :param object_dict:
        :return:
        """
        try:
            msg_str = json.dumps(object_dict)
        except TypeError as exc:
            logging.exception(exc)
            logging.error('Could not convert dict to JSON string for:%r', object_dict)
            return
        for wsock in WEB_SOCKETS:
            wsock.write_message(msg_str)

    @staticmethod
    def emit_signal(message):
        """TBW.

        :param message:
        :return:
        """
        msg = json.loads(message)
        args = msg.get('args', [])
        kwargs = msg.get('kwargs', {})
        signals.dispatcher.emit(sender=msg['sender'], signal=msg['signal'])(*args, **kwargs)

    def on_message(self, message):
        """TBW.

        :param message:
        :return:
        """
        self.emit_signal(message)
        # threading.Thread(target=self.emit_signal, args=[message]).start()


class IndexPageHandler(tornado.web.RequestHandler):
    """The index.html HTML generation handler."""

    def get(self):
        """TBW."""
        self.render("index.html", controller=self.application.controller)


class PipelinePageHandler(tornado.web.RequestHandler):
    """The index.html HTML generation handler."""

    def get(self, name):
        """TBW."""
        self.application.controller.load_template(name)
        self.render("index.html", controller=self.application.controller)


class WebApplication(tornado.web.Application):
    """The Application that host several objects to communicate with."""

    def __init__(self, controller, js9_dir=None, data_dir=None):
        """TBW.

        :param controller:
        """
        self.controller = controller

        handlers = [
            (r'/', IndexPageHandler),
            (r'/pipeline/(.*)', PipelinePageHandler),
            (r'/(favicon\.ico)', tornado.web.StaticFileHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler),
            (r'/websocket', WebSocketHandler),
            (r'/js9/(.*)', tornado.web.StaticFileHandler, {'path': js9_dir}),
            (r'/data/(.*)', tornado.web.StaticFileHandler, {'path': data_dir}),
        ]
        if js9_dir:
            if not os.path.exists(js9_dir):
                raise RuntimeError('js9 directory does not exist: %r' % js9_dir)

        if data_dir:
            if not os.path.exists(data_dir):
                raise RuntimeError('data directory does not exist: %r' % data_dir)

        settings = {
            'template_path': os.path.join(MODULE_DIR, 'template'),
            'static_path': os.path.join(MODULE_DIR, 'static'),
            'debug': True,
            'autoreload': False,
        }
        tornado.web.Application.__init__(self, handlers, **settings)


class TornadoServer(object):
    """The Tornado web server hosting the Application."""

    def __init__(self, app, host_port):
        """TBW.

        :param app:
        :param host_port:
        """
        self._host_port = host_port
        self._th = None
        self._server = None
        self._app = app

    def log_init(self):
        """TBW."""
        host = self._host_port[0]
        if self._host_port[0] == '0.0.0.0':
            host = 'localhost'
        if self._host_port[1] == 80:
            url = 'http://' + host
        else:
            url = 'http://' + host + ':' + str(self._host_port[1])
        logging.info('Navigate to:\n' + url)

    def start(self):
        """TBW."""
        self._th = threading.Thread(target=self.run)
        self._th.start()

    def stop(self):
        """TBW."""
        self.close()

    def run(self):
        """TBW."""
        # ws_app = Application(self._obj)
        self._server = tornado.httpserver.HTTPServer(self._app)
        self._server.listen(self._host_port[1], self._host_port[0])
        self.log_init()
        tornado.ioloop.IOLoop.instance().start()

    def close(self):
        """TBW."""
        tornado.ioloop.IOLoop.instance().stop()
        if self._th:
            self._th.join()
        self._server.stop()
