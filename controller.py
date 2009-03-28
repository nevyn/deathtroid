#!/usr/bin/env python
# encoding: utf-8
"""
controller.py

Created by Joachim Bengtsson on 2009-03-28.
Copyright (c) 2009 Third Cog Software. All rights reserved.
"""

import sys
import os
import model
from BLIP import Connection, Listener, OutgoingRequest
import demjson
import asyncore
import view
import euclid

class ServerController(object):
  """docstring for ServerController"""
  def __init__(self):
    super(ServerController, self).__init__()
    
    self.game = model.Game("foolevel")
    self.game.delegate = self
    
    self.listener = Listener(8245)
    self.listener.onConnected = self.newConnection
    self.connections = []
    
    P = model.Player()
    E = model.Entity(self.game.level, "test player", euclid.Vector2(5,0))
    P.set_entity(E)
    self.game.player = [P]
    
    
  def ful_get_player(self, n):
    return self.game.ful_get_player(n)
  
  def update(self, dt):
    asyncore.loop(timeout=0.01,count=1)
    self.game.update(dt)
  
  # Network
  def newConnection(self, conn):
    self.connections.append(conn)
  
  def broadcast(self, msgName, data):
     payload = demjson.encode(data)
     for c in self.connections:
      req = OutgoingRequest(c, payload, {'Message-Name': msgName})
      req.compressed = True
      print "sending ", req
      req.send()
      
  
  # Model delegates
  def entityChanged(self, entity):
    entityRep = {
      "name": entity.name,
      "pos": [entity.pos.x, entity.pos.y]
    }
  
    self.broadcast("entityChanged", entityRep)

    

class GameController(object):
  """hej"""
  def __init__(self):
    super(GameController, self).__init__()
    
    self.game = model.Game("foolevel")
    self.view = view.View(self.game)
    self.connection = Connection( ('localhost', 8245) )
    self.connection.onRequest = self.incomingRequest
  
  def incomingRequest(self, req):
    msgName = req.properties.get('Message-Name')
    payload = demjson.decode(req.body)
    
    if(msgName == "entityChanged"):
      entity = self.game.level.entity_by_name(payload["name"])
      entity.pos.x = payload["pos"][0]
      entity.pos.y = payload["pos"][1]
  
    
  def update(self, dt):
    asyncore.loop(timeout=0.01,count=1)
  
  def draw(self):
    self.view.draw()
    



"""
class Jocke:
  def __init__(self):
    self.hair_length = 5
    self.procrastination_level = levels.MAX
    
  def frame(self):
    
    self.toilet_need = self.toilet_need + 1
    
    if random.randInt(0, 50) == 3:
      print "Auuurghh"
    else if self.boredom > 10:
      self.fiddle_with_iphone(5)
    
    def fiddle_with_iphone(self, duration):
      self.equip(self.items[IPHONE])
      



jocke = Jocke()

jocke.run()"""