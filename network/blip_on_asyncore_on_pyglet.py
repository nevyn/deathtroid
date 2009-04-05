import struct
import demjson
from BLIP import *
from pyglet import clock
import cPickle as pickle
import threading
import select
import pybonjour

import network

class BLIPOnAsyncoreOnPyglet(network.NetworkInterface):
  """BLIP on top of Asyncore, polled by a pyglet schedule. Asynchronous, out-of-order and very inefficient."""
  def __init__(self):
    super(BLIPOnAsyncoreOnPyglet, self).__init__()
    self.delegate = None
    
  def send(self, connection, msgName, payload):
    req = OutgoingRequest(connection, "",
      {
        "msgName": msgName,
        "payload": pickle.dumps(payload) #demjson.encode(payload)
      })
    req.compressed = True
    req.noReply = True
    return req.send()


  def newData2(self, delegate, msg):
    msgName = msg["msgName"]
    payload = pickle.loads(msg["payload"]) #demjson.decode(msg["payload"])
    delegate.gotData(msg.connection, msgName, payload)

  def startServer(self, name, port, delegate):
    listener = Listener(port)
  
    def register_callback(sdRef, flags, errorCode, name, regtype, domain):
      if errorCode == pybonjour.kDNSServiceErr_NoError:
              print 'Registered service:'
              print '  name    =', name
              print '  regtype =', regtype
              print '  domain  =', domain
            
    def newConnection(conn):
      delegate.newConnection(conn)
  
    def newData(msg):
      self.newData2(delegate, msg)
  
    sdRef = pybonjour.DNSServiceRegister(name = name, regtype = "_deathtroid._tcp", port = port, callBack = register_callback)
  
    listener.onRequest = newData
    listener.onConnected = newConnection
  
    self.startPolling(sdRef)

  def startClient(self, host, port, delegate):
    conn = Connection( (host,port) )
  
    def newData(msg):
      self.newData2(delegate, msg)
  
    conn.onRequest = newData
    delegate.newConnection(conn)
  
    self.startPolling()

  def startPolling(self, sdRef = None):
    clock.schedule(self.poll, sdRef)
    #SelectThread().start()

  def poll(self, asdf, sdRef):
    #asyncore.loop(timeout=0.01, count=2)
    asyncore.poll(0.01)
  
    if sdRef:
      ready = select.select([sdRef], [], [], 0)
      if sdRef in ready[0]:
        pybonjour.DNSServiceProcessResult(sdRef)