import network
import socket as pysocket
import select
import threading, time, struct
import cPickle as pickle
from Queue import Queue

from pyglet import clock


RECVSIZE = 1024*4

class Connection(object):
  def __init__(self, socket):
    self.socket = socket
    self.buffer = ""
    
  def recv(self):
    data = self.socket.recv(RECVSIZE)
    if len(data) == 0:
      return None
    else:
      self.buffer += data
      
      messages = []
      msg = self.nextmessage()
      while msg:
        messages.append(msg)
        msg = self.nextmessage()
      return messages
    return None
    
  def send(self, data):
    data = struct.pack("L", len(data)) + data
    self.socket.send(data)

  def nextmessage(self):
    data = None
    buffer = self.buffer
    if len(buffer) > 4:
      size = struct.unpack("L", buffer[:4])[0]
      if len(buffer) >= 4+size:
        data = buffer[4:size+4]
        self.buffer = buffer[4+size:]
        
    return data
    


class Server(object):
  def __init__(self, net):
    self.socket = pysocket.socket()
    self.socket.setsockopt(pysocket.SOL_SOCKET, pysocket.SO_REUSEADDR, 1)
    self.rlist = [self.socket]
    self.net = net
    self.clients = {}
    
  def listen(self, interface, port):
    self.socket.bind((interface, port))
    self.socket.listen(1)
    
  def accept(self):
    socket, ip = self.socket.accept()
    conn = Connection(socket)
    self.clients[socket] = conn
    self.rlist.append(socket)
    self.net.newconnectionqueue.append(conn)
    
  def run(self):
    while True:
      readlist, writelist, errorlist = select.select(self.rlist, [], [])
      for reader in readlist:
        if reader == self.socket:
          self.accept()
        else:
          conn = self.clients[reader]
          for msg in conn.recv():
            self.net.queue.append((conn,msg))
            
    self.socket.close()
  
class Client(Connection):
  def __init__(self, net):
    super(Client, self).__init__(pysocket.socket())
    self.net = net
    
  def connect(self, host, port):
    self.socket.connect((host, port))
    
  def run(self):
    while True:
      for msg in self.recv():
        self.net.queue.append((self, msg))
    self.socket.close()
  
class Voxnet(network.NetworkInterface):
  def __init__(self):
    super(Voxnet, self).__init__()
    self.queue = []
    self.newconnectionqueue = []
  
  def send(self, connection, msgName, payload):
    """Send a message named msgName to the connection identified by connection. Payload can be any python term serializable by cPickle."""
    msg = pickle.dumps( (msgName, payload) )
    connection.send(msg)
  
  def startServer(self, name, port, delegate):
    """Start a new listen server on port 'port'. The service will be advertised as 'name' on Zeroconf. 'delegate' will be informed of new connections."""
    self.name = name
    self.delegate = delegate
    
    self.net = Server(self)
    self.net.listen("", port)
    
    clock.schedule(self.dispatch)
    
    t = threading.Thread(target=self.net.run)
    t.setDaemon(True)
    t.start()
    
  
  def startClient(self, host, port, delegate):
    """Connect to 'host' on 'port'. 'delegate' will be informed of new incoming data."""
    self.delegate = delegate
    self.net = Client(self)
    
    clock.schedule(self.dispatch)
    
    self.net.connect(host, port)
    self.delegate.newConnection(self.net)
    
    t = threading.Thread(target=self.net.run)
    t.setDaemon(True)
    t.start()
    
    
  def dispatch(self, dt):
#    print "dispatch",self.queue
    queue = self.newconnectionqueue
    self.newconnectionqueue = []
    for newconn in queue:
      self.delegate.newConnection(newconn)
      
      
    queue = self.queue
    self.queue = []
    for conn, msg in queue:
      msgName, payload = pickle.loads(msg)
      self.delegate.gotData(conn, msgName, payload)
      
