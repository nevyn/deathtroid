import twisted
from twisted.internet.protocol import Protocol, Factory, ClientFactory
from twisted.protocols.basic import NetstringReceiver
import pygletreactor
pygletreactor.install() # <- this must come before...
from twisted.internet import reactor, task # <- ...importing this reactor!

import struct
import demjson

class DeathtroidProtocol(NetstringReceiver):
  def connectionMade(self):
    print "connection made"
    self.controller.newConnection(self)
    self.state = "wait for length"
    print "transport", self.transport, type(self.transport)
    self.transport.setTcpNoDelay(True)
    
  
  def stringReceived(self, data):
      unpackedData = data.decode("utf8")
      term = demjson.decode(unpackedData)
      self.controller.gotData(self, term)  
  
  def send(self, messageName, payload):
    d = {
      "Message-Name": messageName,
      "Payload": payload
    }
    
    dd = demjson.encode(d).encode("utf8")
    
    self.sendString(dd)

class DeathtroidServerFactory (Factory):

  protocol = DeathtroidProtocol

  def __init__(self, controller):
    self.controller = controller

  def buildProtocol(self, addr):
    newProto = Factory.buildProtocol(self, addr)
    newProto.controller = self.controller
    return newProto


class DeathtroidClientFactory (ClientFactory):

  protocol = DeathtroidProtocol

  def __init__(self, controller):
    self.controller = controller

  def buildProtocol(self, addr):
    newProto = ClientFactory.buildProtocol(self, addr)
    newProto.controller = self.controller
    return newProto



def startServer(port, ctrlr):
  reactor.listenTCP(port, DeathtroidServerFactory(ctrlr))
  
def startClient(host, port, ctrlr):
  reactor.connectTCP(host, port, DeathtroidClientFactory(ctrlr))

