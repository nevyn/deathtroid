import struct
import demjson
from BLIP import *
from pyglet import clock
import cPickle as pickle

class NetworkDelegate(object):
  def newConnection(connection):
    pass
  def gotData(connection, msgName, payload):
    pass

def send(connection, msgName, payload):
  req = OutgoingRequest(connection, "",
    {
      "msgName": msgName,
      "payload": pickle.dumps(payload) #demjson.encode(payload)
    })
  req.compressed = True
  req.noReply = True
  return req.send()


def newData2(delegate, msg):
  msgName = msg["msgName"]
  payload = pickle.loads(msg["payload"]) #demjson.decode(msg["payload"])
  delegate.gotData(msg.connection, msgName, payload)

def startServer(port, delegate):
  listener = Listener(port)
  def newConnection(conn):
    delegate.newConnection(conn)
  
  def newData(msg):
    newData2(delegate, msg)
  
  listener.onRequest = newData
  listener.onConnected = newConnection
  
  startPolling()

def startClient(host, port, delegate):
  conn = Connection( (host,port) )
  
  def newData(msg):
    newData2(delegate, msg)
  
  conn.onRequest = newData
  delegate.newConnection(conn)
  
  startPolling()

def startPolling():
  clock.schedule_interval(poll, 1./30.)

def poll(asdf):
  asyncore.loop(timeout=0.01, count=2)
      
"""
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
"""
