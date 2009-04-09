import select
import pybonjour
import threading
import struct
import time
  
def dnstxt_to_strings(txt):
  #format: <byte size><data><byte size><data>
  strings = []
  while len(txt) > 1:
    size = ord(txt[0])
    str = txt[1:size+1]
    strings.append(str)
    txt = txt[size+1:]
  return strings
  
def strings_to_dnstxt(strings):
  parts = []
  for item in strings:
    if isinstance(item, unicode):
      item = item.encode('utf-8')
    if len(item) > 255:
      item = item[:255]
    parts.append(chr(len(item)))
    parts.append(item)

  return ''.join(parts)

class BonjourService(object):
  def __init__(self):
    self.ref = None
    self.timeout = None
    
  def close(self):
    self.ref.close()
    
  def poll(self, timeout=None):
    rlist = select.select([self.ref], [], [], timeout)[0]
    for ref in rlist:
      pybonjour.DNSServiceProcessResult(ref)
      
  def run(self):
    self.running = True
    while self.running:
      self.poll(self.timeout)
    self.close()
      
  def start(self):
    self.thread = threading.Thread(target=self.run)
    self.thread.setDaemon(True)
    self.thread.start()
      
class RegisterService(BonjourService):
  def __init__(self, name, type, protocoll, port, txtList=None, regtype=None):
    super(RegisterService, self).__init__()
    regtype = regtype or "_%s._%s"%(type, protocoll)
    print  name, type, protocoll, port, regtype
    if txtList: txtList = strings_to_dnstxt(txtList)
    self.ref = pybonjour.DNSServiceRegister(name=name, regtype=regtype, port=port, txtRecord=txtList, callBack=self.callback)
    
  def update(self, newText, ttl=10000):
    newText = strings_to_dnstxt(newText)
    print "update",pybonjour.DNSServiceUpdateRecord(self.ref, RecordRef=None, flags=0, rdata=newText, ttl=ttl)

  def callback(self, sdRef, flags, errorCode, name, regtype, domain):
    if errorCode == pybonjour.kDNSServiceErr_NoError:
      self.on_registered(name, regtype, domain)
    else:
      self.on_error("some error while registering service")
      
  def on_error(self, info):
    print "register error:",info
      
  def on_registered(self, name, regtype, domain):
    print 'Registered service:'
    print '  name    =', name
    print '  regtype =', regtype
    print '  domain  =', domain
    
class BrowseService(BonjourService):
  def __init__(self, type, protocoll, regtype=None):
    super(BrowseService, self).__init__()
    regtype = regtype or "_%s._%s"%(type, protocoll)
    print "fenkfnek", regtype
    self.ref = pybonjour.DNSServiceBrowse(regtype=regtype, callBack=self.callback)
    
    
  def callback(self, sdRef, flags, interfaceIndex, errorCode, serviceName, regtype, replyDomain):
    if errorCode != pybonjour.kDNSServiceErr_NoError:
      self.on_error("some error...")

    elif (flags & pybonjour.kDNSServiceFlagsAdd):
      self.on_service_added(interfaceIndex, serviceName, regtype, replyDomain)
      
    else:
      self.on_service_removed(serviceName, regtype, replyDomain)
    
  def on_error(self, info):
    print "Error",info
    
  def on_service_added(self, interfaceIndex, serviceName, regtype, replyDomain):
    print 'Service added; resolving',info
    
  def on_service_removed(self, *info):
    print 'Service removed',info
      
class ResolveService(BonjourService):
  def __init__(self, interfaceIndex, serviceName, regtype, replyDomain):
    super(ResolveService, self).__init__()
    self.ref = pybonjour.DNSServiceResolve(0, interfaceIndex, serviceName, regtype, replyDomain, self.callback)
    
  def callback(self, sdRef, flags, interfaceIndex, errorCode, fullname, hosttarget, port, txtRecord):
    if errorCode == pybonjour.kDNSServiceErr_NoError:
      self.on_resolved(fullname, hosttarget, port, dnstxt_to_strings(txtRecord))
    else:
      self.on_error("Some error while resolving")
      
  def on_error(self, info):
    print "error:", info
    
  def on_resolved(self, fullname, hosttarget, port, txtRecord):
    print 'Resolved service:'
    print '  fullname   =', fullname
    print '  hosttarget =', hosttarget
    print '  port       =', port
    print '  txt        =', txtRecord
    
    
def find(atype, protocoll="tcp", timeout=2):
  found = []
  def br(interfaceIndex, serviceName, regtype, replyDomain):
    found.append( (interfaceIndex, serviceName, regtype, replyDomain) )
  browser = BrowseService(atype, protocoll)
  browser.on_service_added = br
  t = tt = time.time()
  while time > 0:
    tt -= time.time()-t
    browser.poll(tt)
  return found

def find_and_resolve(atype, protocoll="tcp", timeout=2):
  """Browse for and return all services we can find within time"""
  found = []
  def br(interfaceIndex, serviceName, regtype, replyDomain):
    def res(fullname, hosttarget, port, txtRecord):
      found.append( (fullname, hosttarget, port, txtRecord) )
    resolv = ResolveService(interfaceIndex, serviceName, regtype, replyDomain)
    resolv.on_resolved = res
    resolv.poll(timeout)
  browser = BrowseService(atype, protocoll)
  browser.on_service_added = br
  while timeout > 0:
    t = time.time()
    browser.poll(timeout)
    timeout -= time.time()-t
  return found
    
if __name__ == "__main__":
  def br(interfaceIndex, serviceName, regtype, replyDomain):
    print "****"
    resolv = ResolveService(interfaceIndex, serviceName, regtype, replyDomain)
    resolv.poll(5)
    
  reg = RegisterService("hello", "testing", "tcp", 12345, ["players=2", "player1=voxar", "player2=sterd"])
  browse = BrowseService("testing", "tcp")
  browse.on_service_added = br
  import time
  t = time.time()
  def run():
    global browse
    update=True
    while True:
      if update and time.time()-t > 5:
        update = False
        reg.update(['Hello world'])

      reg.poll(0)
      browse.poll(0)
    

  #threading.Thread(target=run).start()
  run()
