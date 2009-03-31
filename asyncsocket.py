# encoding: utf-8
"""
asyncsocket.py

Created by Joachim Bengtsson on 2009-03-31.
Copyright (c) 2009 Third Cog Software. All rights reserved.
"""

import threading


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
  
  2

    /**
     * Called when a socket accepts a connection.  Another socket is spawned to handle it. The new socket will have
     * the same delegate and will call "onSocket:didConnectToHost:port:".
    **/
    - (void)onSocket:(AsyncSocket *)sock didAcceptNewSocket:(AsyncSocket *)newSocket;

    /**
     * Called when a new socket is spawned to handle a connection.  This method should return the run-loop of the
     * thread on which the new socket and its delegate should operate. If omitted, [NSRunLoop currentRunLoop] is used.
    **/
    - (NSRunLoop *)onSocket:(AsyncSocket *)sock wantsRunLoopForNewSocket:(AsyncSocket *)newSocket;

    /**
     * Called when a socket is about to connect. This method should return YES to continue, or NO to abort.
     * If aborted, will result in AsyncSocketCanceledError.
     * 
     * If the connectToHost:onPort:error: method was called, the delegate will be able to access and configure the
     * CFReadStream and CFWriteStream as desired prior to connection.
     *
     * If the connectToAddress:error: method was called, the delegate will be able to access and configure the
     * CFSocket and CFSocketNativeHandle (BSD socket) as desired prior to connection. You will be able to access and
     * configure the CFReadStream and CFWriteStream in the onSocket:didConnectToHost:port: method.
    **/
    - (BOOL)onSocketWillConnect:(AsyncSocket *)sock;

    /**
     * Called when a socket connects and is ready for reading and writing.
     * The host parameter will be an IP address, not a DNS name.
    **/
    - (void)onSocket:(AsyncSocket *)sock didConnectToHost:(NSString *)host port:(UInt16)port;

    /**
     * Called when a socket has completed reading the requested data into memory.
     * Not called if there is an error.
    **/
    - (void)onSocket:(AsyncSocket *)sock didReadData:(NSData *)data withTag:(long)tag;

    /**
     * Called when a socket has read in data, but has not yet completed the read.
     * This would occur if using readToData: or readToLength: methods.
     * It may be used to for things such as updating progress bars.
    **/
    - (void)onSocket:(AsyncSocket *)sock didReadPartialDataOfLength:(CFIndex)partialLength tag:(long)tag;

    /**
     * Called when a socket has completed writing the requested data. Not called if there is an error.
    **/
    - (void)onSocket:(AsyncSocket *)sock didWriteDataWithTag:(long)tag;

    /**
     * Called after the socket has completed SSL/TLS negotiation.
     * This method is not called unless you use the provided startTLS method.
    **/
    - (void)onSocket:(AsyncSocket *)sock didSecure:(BOOL)flag;
  