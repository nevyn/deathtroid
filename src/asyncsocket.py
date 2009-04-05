# encoding: utf-8
"""
asyncsocket.py

Created by Joachim Bengtsson on 2009-03-31.
Copyright (c) 2009 Third Cog Software. All rights reserved.
"""

import threading
import socket



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
    self.delegate = delegate
  
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
    pass
  
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
    pass
    
  def progressOfWrite(self, tag):
    pass
    
  
  def unreadData(self):
    """/**
     * In the event of an error, this method may be called during onSocket:willDisconnectWithError: to read
     * any data that's left on the socket.
    **/"""
    pass
  
    
    
    
    
    