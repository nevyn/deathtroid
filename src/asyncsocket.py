# encoding: utf-8
"""
asyncsocket.py

Created by Joachim Bengtsson on 2009-03-31.
Copyright (c) 2009 Third Cog Software. All rights reserved.
"""

import threading
import socket

readQueueCapacity = 5
writeQueueCapacity = 5
readallChunksize = 256
writeChunksize = 1024*4

kEnablePreBuffering      = 1 << 0  #// If set, pre-buffering is enabled
kDidPassConnectMethod    = 1 << 1  #// If set, disconnection results in delegate call
kDidCallConnectDelegate  = 1 << 2  #// If set, connect delegate has been called
kStartingTLS             = 1 << 3  #// If set, we're waiting for TLS negotiation to complete
kForbidReadsWrites       = 1 << 4  #// If set, no new reads or writes are allowed
kDisconnectAfterReads    = 1 << 5  #// If set, disconnect after no more reads are queued
kDisconnectAfterWrites   = 1 << 6  #// If set, disconnect after no more writes are queued
kClosingWithError        = 1 << 7  #// If set, the socket is being closed due to an error

DEFAULT_PREBUFFERING = True


class AsyncSocketDelegate(object):
  """This class is just for showing a sample AsyncSocket delegate implementation."""
  
  def socketWillDisconnectWithError(self, socket, error):
    """/**
     * In the event of an error, the socket is closed.
     * You may call "unreadData" during this call-back to get the last bit of data off the socket.
     * When connecting, this delegate method may be called
     * before"onSocket:didAcceptNewSocket:" or "onSocket:didConnectToHost:".
    **/
    """
    pass
  
  def onSocketDidDisconnect(self, socket):
    """/**
     * Called when a socket disconnects with or without error.  If you want to release a socket after it disconnects,
     * do so here. It is not safe to do that during "onSocket:willDisconnectWithError:".
    **/"""
    pass
  
  def onSocketDidAcceptNewSocket(self, socket, newSocket):
    """/**
     * Called when a socket accepts a connection.  Another socket is spawned to handle it. The new socket will have
     * the same delegate and will call "onSocket:didConnectToHost:port:".
    **/"""
    pass
  
  def onSocketWantsRunLoopForNewSocket(self, socket):
    """/**
     * Called when a new socket is spawned to handle a connection.  This method should return the run-loop of the
     * thread on which the new socket and its delegate should operate. If omitted, [NSRunLoop currentRunLoop] is used.
    **/"""
    pass
    
  def onSocketWillConnect(self, socket):
    """/**
     * Called when a socket is about to connect. This method should return YES to continue, or NO to abort.
     * If aborted, will result in AsyncSocketCanceledError.
     * 
     * If the connectToHost:onPort:error: method was called, the delegate will be able to access and configure the
     * CFReadStream and CFWriteStream as desired prior to connection.
     *
     * If the connectToAddress:error: method was called, the delegate will be able to access and configure the
     * CFSocket and CFSocketNativeHandle (BSD socket) as desired prior to connection. You will be able to access and
     * configure the CFReadStream and CFWriteStream in the onSocket:didConnectToHost:port: method.
    **/"""
    pass
  
  def onSocketDidConnectToHost(self, socket, host, port):
    """/**
     * Called when a socket connects and is ready for reading and writing.
     * The host parameter will be an IP address, not a DNS name.
    **/"""
    pass
  
  def onSocketDidReadDataWithTag(self, socket, data, tag):
    """/**
     * Called when a socket has completed reading the requested data into memory.
     * Not called if there is an error.
    **/"""
    pass
  
  def onSocketDidReadPartialDataOfLengthWithTag(self, socket, length, tag):
    """/**
     * Called when a socket has read in data, but has not yet completed the read.
     * This would occur if using readToData: or readToLength: methods.
     * It may be used to for things such as updating progress bars.
    **/"""
    pass
  
  def onSocketDidWriteDataWithTag(self, socket, tag):
    """/**
     * Called when a socket has completed writing the requested data. Not called if there is an error.
    **/"""
    pass

class AsyncSocket(object):
  """Aynchronous socket handling."""
  def __init__(self, delegate=None):
    super(AsyncSocket, self).__init__()
    self.flags = kEnablePreBuffering if DEFAULT_PREBUFFERING else 0
    self.delegate = delegate
    
    self.socket = None
    self.source = None
    self.socket6 = None
    self.source6 = None
    self.runLoop = None
    self.readStream = None
    self.writeStream = None
    
    self.readQueue = []
    self.currentRead = None
    self.readTimer = None
    
    self.partialReadBuffer = ""
    
    self.writeQueue = []
    self.currentWrite = None
    self.writeTimer = None
  
  def delegate():
      doc = "The delegate; any instance implementing any part of the AsyncSocketDelegate protocol. Only set the delegate when it's safe"
      def fget(self):
          return self._delegate
      def fset(self, value):
          self._delegate = value
      def fdel(self):
          del self._delegate
      return locals()
  delegate = property(**delegate())
  
  def canSafelySetDelegate(self):
    return len(self.readQueue) == 0 and len(self.writeQueue) == 0 and self.currentRead = None and self.currentWrite = None
  
  
    
  
  #/**
  #   * Once one of these methods is called, the AsyncSocket instance is locked in, and the rest can't be called without
  #   * disconnecting the socket first.  If the attempt times out or fails, these methods either return NO or
  #   * call "onSocket:willDisconnectWithError:" and "onSockedDidDisconnect:".
  #  **/
  def acceptOnPort(self, port, address=None):
    pass
  
  def connectToHostOnPort(self, host, port):
    pass
  
  def disconnect(self):
    """Disconnects immediately. After this, read and write calls will do nothing. Any pending reads or writes are dropped."""
    pass
  
  def disconnectAfterReading(self):
    """Wait until all pending reads are done, then disconnect. After this, read and write calls will do nothing. Remaining writes will be discarded."""
    pass
    
  def disconnectAfterWriting(self):
    """Wait until all pending writes are done, then disconnect. After this, read and write calls will do nothing. Remaining reads will be discarded."""
    pass
  
  def disconnectAfterReadingAndWriting(self):
    """Wait until all pending reads and writes are done, then disconnect. After this, read and write calls will do nothing."""
    pass
  
  def isConnected(self):
    """Returns True if the socket and streams are open, connected, and ready for reading and writing."""
    pass
  
  def connectedHost(self):
    """Returns the local or remote host to which this socket is connected, or None if not connected. The host will be an IP adress."""
    pass
    
  def connectedPort(self):
    """Returns the local or remote port to which this socket is connected, or None if not connected."""
    pass
  
  #// The readData and writeData methods won't block. To not time out, use a negative time interval.
  #// If they time out, "onSocket:disconnectWithError:" is called. The tag is for your convenience.
  #// You can use it as an array index, step number, state id, pointer, etc., just like the socket's user data.
  
  def readDataToLength(self, length, timeout = -1., tag = None):
    """/**
     * This will read a certain number of bytes into memory, and call the delegate method when those bytes have been read.
     * If there is an error, partially read data is lost.
     * If the length is 0, this method does nothing and the delegate is not called.
    **/"""
  
  def readDataToSeparator(self, separator, maxLength = -1, timeout = -1., tag = None):
    """/**
     * This reads bytes until (and including) the passed "separator" stringbuffer parameter, which acts as a separator.
     * The bytes and the separator are returned by the delegate method.
     * 
     * If you pass None or zero-length data as the "separator" parameter,
     * the method will do nothing, and the delegate will not be called.
     *
     * If the max length is surpassed, it is treated the same as a timeout - the socket is closed.
     * 
     * To read a line from the socket, use the line separator (e.g. CRLF for HTTP, see below) as the "separator" parameter.
     * Note that this method is not character-set aware, so if a separator can occur naturally as part of the encoding for
     * a character, the read will prematurely end.
    **/"""

  def readData(self, timeout = -1., tag = None):
    """/**
     * Reads the first available bytes that become available on the socket.
    **/"""
    pass
  
  def writeData(self, data, timeout = -1, tag = None):
    """/**
     * Writes data to the socket, and calls the delegate when finished.
     * 
     * If you pass in None or zero-length data, this method does nothing and the delegate will not be called.
    **/"""
  
  def progressOfRead(self, tag):
    if not self.currentRead:
      return -1
    
  def progressOfWrite(self, tag):
    pass
    
  
  def unreadData(self):
    """/**
     * In the event of an error, this method may be called during onSocket:willDisconnectWithError: to read
     * any data that's left on the socket.
    **/"""
    pass
  

######## Private
class AsyncReadPacket(object):
  """The AsyncReadPacket encompasses the instructions for any given read.
  The contents of a read packet allows the code to determine if we're:
  - reading to a certain length
  - reading to a certain separator
  - or simply reading the first chunk of available data"""
  def __init__(self, buf, timeout, tag, readAllAvailableData, terminator, maxLength):
    super(AsyncReadPacket, self).__init__()
    self.buf = buf
    self.timeout = timeout
    self.tag = tag
    self.readAllAvailableData = readAllAvailableData
    self.terminator = terminator
    self.maxLength = maxLength
    
    self.bytesDone = 0


  
  def readLengthForTerm(self):
    """* For read packets with a set terminator, returns the safe length of data that can be read
    * without going over a terminator, or the maxLength.
    * 
    * It is assumed the terminator has not already been read."""
    result = len(self.terminator)
    
    if result == 1:
      return result
    
    i = max(0, (self.bytesDone - len(self.terminator) + 1))
    j = min(len(self.terminator) - 1, self.bytesDone)
    
    while i < self.bytesDone:
      subBuffer = self.buf[i:]
      if subBuffer == self.terminator:
        result = len(self.terminator) - j
        break
      
      i += 1
      j -= 1
    if self.maxLength > 0:
      return min(result, (self.maxLength - self.bytesDone))
    else
      return result
  
  def prebufferReadLengthForTerm(self):
    """
    * without going over the maxLength.
    * Assuming pre-buffering is enabled, returns the amount of data that can be read
    """
    if self.maxLength > 0:
      return min(readallChunksize, (self.maxLength - self.bytesDone))
    else:
      return readallChunksize
  
  def searchForTermAfterPreBuffering(self, numBytes):
    """* For read packets with a set terminator, scans the packet buffer for the term.
    * It is assumed the terminator had not been fully read prior to the new bytes.
    * 
    * If the term is found, the number of excess bytes after the term are returned.
    * If the term is not found, this method will return -1.
    * 
    * Note: A return value of zero means the term was found at the very end.
    """
    
    if self.terminator == nil:
      raise "Searching for term in data when there is no term."
    
    i = max(0, (self.bytesDone - numBytes - len(self.terminator) + 1))
    
    while i + len(self.terminator) <= self.bytesDone:
      subBuffer = self.buffer[i:]
      
      if subBuffer == self.terminator:
        return self.bytesDone - (i + len(self.terminator))
        
      i += 1
    
    return -1

class AsyncWritePacket(object):
  """The AsyncWritePacket encompasses the instructions for any given write"""
  def __init__(self, data, timeout, tag):
    super(AsyncWritePacket, self).__init__()
    self.data = data
    self.timeout = timeout
    self.tag = tag
    self.bytesDone = 0


    
  
  
    
    
    
    
    