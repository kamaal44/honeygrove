from honeygrove import log
from honeygrove.config import Config
from honeygrove.services.ServiceBaseModel import Limiter, ServiceBaseModel

from twisted.conch.telnet import TelnetTransport, StatefulTelnetProtocol
from twisted.internet import protocol

import time


class TelnetService(ServiceBaseModel):
    def __init__(self):
        super(TelnetService, self).__init__()

        self._name = Config.telnet.name
        self._port = Config.telnet.port

        self._fService = TelnetFactory()

        self._limiter = Limiter(self._fService, Config.telnet.name, Config.telnet.connections_per_host)


class TelnetProtocol(StatefulTelnetProtocol):
    # This is required as we are stateful and this gets set to "Password" after on_username returns
    state = "User"

    def on_new_connection(self):
        response = "Username: "
        self.transport.write(response.encode("UTF-8"))
        self.peer = self.transport.getPeer().host

    def on_username(self, line):
        self.username = line.decode("UTF-8")
        response = "Password: "
        self.transport.write(response.encode("UTF-8"))
        return "Password"

    def on_password(self, line):
        self.password = line.decode("UTF-8")

        log.login(Config.telnet.name, self.peer, Config.telnet.port, False, self.username, self.password, "")

        time.sleep(2.0)

        response = "\nAuthentication failed\nUsername: "
        self.transport.write(response.encode("UTF-8"))

        self.state = "User"
        return "Discard"

    # Twisted requires these exact method names on the class so we rebind them
    connectionMade = on_new_connection
    telnet_User = on_username
    telnet_Password = on_password


class TelnetFactory(protocol.ServerFactory):
    def protocol(_):
        return TelnetTransport(TelnetProtocol)
