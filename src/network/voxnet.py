import network
import socket as pysocket
import select
import threading, time, struct
import cPickle as pickle
from Queue import Queue

from pyglet import clock


RECVSIZE = 1024*4

class ConnectionLost(RuntimeError):
  pass

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
    self.running = False
    
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
    self.running = True
    while self.running:
      self.tick()
    self.socket.close()
    
  def tick(self, timeout=None):
    readlist, writelist, errorlist = select.select(self.rlist, [], [], timeout)
    for reader in readlist:
      if reader == self.socket:
        self.accept()
      else:
        conn = self.clients.get(reader, None)
        if conn:
          try:
            msgs = conn.recv()
            if msgs:
              for msg in msgs:
                self.net.queue.append((conn,msg))
          except pysocket.error, e:
            del self.clients[reader] #remove connection
            self.rlist.remove(reader)
            self.net.connectionLost(conn, e) #tell my master
        else:
          print "::::: the connection did not exist", reader
          
  
class Client(Connection):
  def __init__(self, net):
    super(Client, self).__init__(pysocket.socket())
    self.net = net
    self.running = False
    
  def connect(self, host, port):
    self.socket.connect((host, port))
    
  def run(self):
    self.running = True
    while self.running:
      self.tick()
    try:
      self.socket.close()
    except:
      pass #if socket allready closed
    
  def tick(self, timeout=None):
    rl = select.select([self.socket], [], [], timeout)[0]
    if rl:
      try:
        msgs = self.recv()
        if msgs:
          for msg in msgs:
            self.net.queue.append((self, msg))
      except pysocket.error, e:
        #Connection closed
        self.net.connectionLost(self, e)
  
  
class Voxnet(network.NetworkInterface):
  def __init__(self):
    super(Voxnet, self).__init__()
    self.queue = []
    self.newconnectionqueue = []
    self.thread = None
    self.is_server = False
    
  #interface
  
  def send(self, connection, msgName, payload):
    """Send a message named msgName to the connection identified by connection. Payload can be any python term serializable by cPickle."""
    msg = pickle.dumps( (msgName, payload) )
    try:
      connection.send(msg)
    except pysocket.error, e:
      print "Voxnet::send error",e
      #probably not send lostConnection here. Will be handled by recv but a send might happen after anyways
  
  def startServer(self, name, port, delegate):
    """Start a new listen server on port 'port'. The service will be advertised as 'name' on Zeroconf. 'delegate' will be informed of new connections."""
    self.is_server = True
    self.name = name
    self.delegate = delegate
    
    self.net = Server(self)
    self.net.listen("", port)
    
    clock.schedule(self.dispatch)
    
    self.startThread()
    
    import zeroconf
    zeroconf.RegisterService(name, "deathtroid", "tcp", port).start()
    
  def startClient(self, host, port, delegate):
    """Connect to 'host' on 'port'. 'delegate' will be informed of new incoming data."""
    self.delegate = delegate
    self.net = Client(self)
    
    clock.schedule(self.dispatch)
    
    self.net.connect(host, port)
    self.delegate.newConnection(self.net)
    
    self.startThread()
  
  
  #private  
  def connectionLost(self, conn, reason):
    """Client or a server connection was lost"""
    self.delegate.lostConnection(conn, reason)
    if not self.is_server and self.thread:
      self.net.running = False

    
  def startThread(self):
    #Use this OR self.net.tick(0) (dispatch)
    t = threading.Thread(target=self.net.run)
    t.setDaemon(True)
    t.start()
    self.thread = t
    
  def dispatch(self, dt):
    t = time.time()
    
    #zeroconf
    
    #self.net.tick(0) #Use this OR threads (startThread)
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
  #  print "dispatch time:%.10f"%((time.time()-t)*1000)
      
