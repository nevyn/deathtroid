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
import random

class ServerController(object):
  """docstring for ServerController"""
  def __init__(self):
    super(ServerController, self).__init__()
    
    self.game = model.Game("foolevel")
    self.game.delegate = self
    
    self.listener = Listener(8245)
    self.listener.onConnected = self.newConnection
      
  def update(self, dt):
    asyncore.loop(timeout=0.01,count=1)
    self.game.update(dt)
  
  # Network
  def newConnection(self, conn):
    player = self.game.player_by_connection(conn)
    
    loginRequest = OutgoingRequest(conn, "''", {'Message-Name': 'pleaseLogin'})
    loginRequest.response.onComplete = self.gotLogin
    loginRequest.send()
    print "please login"
  
  def gotLogin(self, response):
    print "someone logged in"
    payload = demjson.decode(response.body)
    name = payload["name"]
    
    player = self.game.player_by_connection(response.connection)
    player.name = name
    
    self.playerChanged(player)
    
    E = model.Entity(self.game.level, "player "+name, euclid.Vector2(random.randint(0, 5),0))
    player.set_entity(E)

    
  
  def broadcast(self, msgName, data):
    payload = demjson.encode(data)
    
    for p in self.game.players:
      c = p.connection
      req = OutgoingRequest(c, payload, {'Message-Name': msgName})
      req.compressed = True
      req.send()
      
  
  # Model delegates
  def entityChanged(self, entity):
    entityRep = {
      "name": entity.name,
      "pos": [entity.pos.x, entity.pos.y]
    }
  
    self.broadcast("entityChanged", entityRep)
  
  def playerChanged(self, player):
    pass
    

class GameController(object):
  """hej"""
  def __init__(self, name):
    super(GameController, self).__init__()
    
    self.name = name
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
    elif(msgName == "pleaseLogin"):
      print "I should log in"
      resp = req.response
      resp.properties['Message-Name'] = "login"
      resp.body = demjson.encode({"name": self.name})
      resp.send()
      
  
  def action(self, what):
    pass
    
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