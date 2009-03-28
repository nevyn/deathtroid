# encoding: utf-8
"""
controller.py

Created by Joachim Bengtsson on 2009-03-28.
Copyright (c) 2009 Third Cog Software. All rights reserved.
"""

import sys
import os
import model
import demjson
import asyncore
import view
import euclid
import random

import twisted
from twisted.internet.protocol import Protocol, Factory
import pygletreactor
pygletreactor.install() # <- this must come before...
from twisted.internet import reactor, task # <- ...importing this reactor!

import resources
from network import *

from twisted.internet.protocol import ClientCreator


class DeathtroidFactory (Factory):
  
  protocol = DeathtroidProtocol
  
  def __init__(self, controller):
    self.controller = controller
  
  def buildProtocol(self, addr):
    newProto = Factory.buildProtocol(self, addr)
    newProto.controller = self.controller
    return newProto
  

class ServerController(object):
  """docstring for ServerController"""
  def __init__(self):
    print "Starting server"
    super(ServerController, self).__init__()
    
    self.game = model.Game("foolevel")
    self.game.delegate = self
    
    reactor.listenTCP(18245, DeathtroidFactory(self))
    print "Server is running"
    
      
  def update(self, dt):
    self.game.update(dt)
  
  def close(self):
    pass
  
  # Network
  
  def gotData(self, connection, term):
    msgName = term["Message-Name"]
    payload = term["Payload"]
    
    if msgName == "login":
      self.gotLogin(connection, payload)
    elif msgName == "player_action":
      player = self.game.player_by_connection(connection)

      pe = player.entity

      cmd = payload["action"]
      if(cmd == "move_left"):
        pe.set_movement(-24,0)
        pe.state = "running_left"
      elif(cmd == "move_right"):
        pe.set_movement(24,0)
        pe.state = "running_right"
      elif(cmd == "jump"):
        if pe.can_jump():
          pe.jump(-2500)
      elif(cmd == "stop_moving_left"):
        pe.set_movement(24,0)
      elif(cmd == "stop_moving_right"):
        pe.set_movement(-24,0)
      elif(cmd == "stop_jump"):
        pe.jump(0)
    
    else:
      print "Unknown message:", payload
    
  
  def newConnection(self, conn):
    print "NEW CONNECTION ", conn
    player = self.game.player_by_connection(conn)
    
    conn.send("pleaseLogin", {})
    
    print "please login"
  
  def gotLogin(self, connection, payload):
    print "someone logged in"
    
    name = payload["name"]
    
    player = self.game.player_by_connection(connection)
    player.name = name
    
    self.playerChanged(player)
    
    E = model.Entity(self.game.level, "player "+name, euclid.Vector2(random.randint(1, 10),2))
    player.set_entity(E)
    
  def broadcast(self, msgName, data):
    payload = demjson.encode(data)
    
    for p in self.game.players:
      c = p.connection
      c.send(msgName, data)
      
  
  # Model delegates
  def entityChanged(self, entity):
    entityRep = {
      "name": entity.name,
      "pos": [entity.pos.x, entity.pos.y],
      "state": entity.state
    }
  
    self.broadcast("entityChanged", entityRep)
  
  def playerChanged(self, player):
    pass
    
