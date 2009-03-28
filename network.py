import twisted
from twisted.internet.protocol import Protocol, Factory
import struct
import demjson

class DeathtroidProtocol(Protocol):
    
  
  def connectionMade(self):
    print "connection made"
    self.controller.newConnection(self)
    self.state = "wait for length"
    
  def dataReceived(self, data):
    if self.state == "wait for length":
      self.state = "wait for data"
      justTheLength = data[:4]

      (length, ) = struct.unpack("L", justTheLength)
      self.incomingDataLength = length
      self.buffer = ""

      rest = data[4:]
      self.dataReceived(rest)
    else:
      dataLength = len(data)

      if dataLength < self.incomingDataLength:
        self.buffer += data
        self.incomingDataLength -= dataLength
        return
      
      data = self.buffer + data
      self.buffer = ""
      
      myData = data[:self.incomingDataLength]
      rest = data[self.incomingDataLength:]
      
      unpackedData = myData.decode("utf8")
      
      term = demjson.decode(unpackedData)

      self.state = "wait for length"
      
      self.controller.gotData(self, term)
      
      if len(rest) > 0:
        self.dataReceived(rest)
      
  
  def send(self, messageName, payload):
    d = {
      "Message-Name": messageName,
      "Payload": payload
    }
    
    dd = demjson.encode(d).encode("utf8")
    length = len(dd)
    out = struct.pack("L", length) + dd

    print "sending", dd, len(out)
    self.transport.write(out)