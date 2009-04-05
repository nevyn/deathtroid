import struct
import demjson
from BLIP import *
from pyglet import clock
import cPickle as pickle
import threading
import select
import pybonjour

class NetworkDelegate(object):
  def newConnection(connection):
    """A Network instance in server mode has received a new connection. The 'connection' object is opaque; only use it to specify who you want to send to when sending data, and to see who you gotData from."""
    pass
  def gotData(connection, msgName, payload):
    """Data has arrived from 'connection' with the name msgName and the python object 'payload'."""
    pass

class NetworkInterface(object):
  """Common interface for all the Network implementations"""
  def __init__(self):
    super(NetworkInterface, self).__init__()
  
  def send(self, connection, msgName, payload):
    """Send a message named msgName to the connection identified by connection. Payload can be any python term serializable by cPickle."""
    raise "Missing implementation"
  
  def startServer(self, name, port, delegate):
    """Start a new listen server on port 'port'. The service will be advertised as 'name' on Zeroconf. 'delegate' will be informed of new connections."""
    raise "Missing implementation"
  
  def startClient(self, host, port, delegate):
    """Connect to 'host' on 'port'. 'delegate' will be informed of new incoming data."""
    raise "Missing implementation"



__all__ = ["blip_on_asyncore_on_pyglet", "twisted_on_pyglet"]


import blip_on_asyncore_on_pyglet
#import twisted_on_pyglet
BestNetwork = blip_on_asyncore_on_pyglet.BLIPOnAsyncoreOnPyglet
  
