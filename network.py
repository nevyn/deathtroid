import twisted
from twisted.protocols.basic import NetstringReceiver
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

