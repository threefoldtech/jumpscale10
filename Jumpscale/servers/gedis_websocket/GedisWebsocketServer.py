from Jumpscale import j
import time
import json
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from collections import OrderedDict

JSConfigClient = j.application.JSBaseConfigClass


class GedisWebsocketServer(JSConfigClient):
    _SCHEMATEXT = """
        @url = jumpscale.gedis.websocket.1
        name* = "default" (S)
        port = 4444
        ssl = True (B)
        ssl_keyfile = "/etc/ssl/resty-auto-ssl-fallback.key" (S)
        ssl_certfile = "/etc/ssl/resty-auto-ssl-fallback.crt" (S)
        """

    def _init(self, **kwargs):
        self._server = None
        self._app = None
        if self.ssl:
            if not j.sal.fs.exists(self.ssl_keyfile):
                raise RuntimeError('SSL: keyfile not exists')
            if not j.sal.fs.exists(self.ssl_certfile):
                raise RuntimeError('SSL: certfile not exists')

    @property
    def server(self):
        if not self._server:

            if self.ssl:
                self._server = WebSocketServer(
                    ("0.0.0.0", self.port),
                    Resource(OrderedDict([("/", Application)])),
                    keyfile=self.ssl_keyfile,
                    certfile=self.ssl_certfile
                )
            else:
                self._server = WebSocketServer(
                    ("0.0.0.0", self.port),
                    Resource(OrderedDict([("/", Application)])))

        return self._server

    @property
    def app(self):
        if not self._app:
            self._app = Application
        return self._app

    def start(self, name="websocket"):
        """
        kosmos 'j.servers.gedis_websocket.start()'
        :param manual means the server is run manually using e.g. kosmos 'j.servers.rack.start()'
        """

        self.server.start()

    def test(self):
        self.default.start()
        self.default.stop()


class Application(WebSocketApplication):
    def on_message(self, message):
        print(message)
        if message is None:
            return

        data = json.loads(message)
        commands = data["command"].split(".")
        if data["command"].casefold() == "system.ping":
            self.ws.send(j.data.serializers.json.dumps(self.client_gedis.ping()))
            return
        cl = getattr(self.client_gedis.actors, commands[0])

        for attr in commands[1:]:
            cl = getattr(cl, attr)

        args = data.get("args", {})

        response = cl(**args)
        if isinstance(response, dict):
            self.ws.send(j.data.serializers.json.dumps(response))
        elif hasattr(response, "_json"):
            self.ws.send(j.data.serializers.json.dumps(response._ddict_hr))
        elif isinstance(response, bytes):
            self.ws.send(response.decode())
        elif response is None:
            self.ws.send("")
        else:
            self.ws.send(response)

    def on_close(self, reason):
        print(reason)

    def on_open(self):
        self.client_gedis = j.clients.gedis.get("main", port=8900)
