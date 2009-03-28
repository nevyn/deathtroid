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
import resources

class ServerController(object):
  """docstring for ServerController"""
  def __init__(self):
    super(ServerController, self).__init__()
    
    self.game = model.Game("foolevel")
    self.game.delegate = self
    
    self.listener = Listener(18245)
    self.listener.onConnected = self.newConnection
      
  def update(self, dt):
    asyncore.loop(timeout=0.01,count=1)
    self.game.update(dt)
  
  def close(self):
    self.listener.close()
    for p in self.game.players:
      p.connection.close()
  
  # Network
  def newConnection(self, conn):
    player = self.game.player_by_connection(conn)
    
    conn.onRequest = self.gotPlayerRequest
    
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
    
    E = model.Entity(self.game.level, "player "+name, euclid.Vector2(random.randint(1, 10),2))
    player.set_entity(E)
  
  def gotPlayerRequest(self, req):
    msgName = req.properties.get('Message-Name')
    payload = demjson.decode(req.body)
    
    if msgName == "player_action":
      player = self.game.player_by_connection(req.connection)
      
      pe = player.entity
      
      cmd = payload["action"]
      if(cmd == "move_left"):
        pe.set_movement(-24,0)
      elif(cmd == "move_right"):
        pe.set_movement(24,0)
      elif(cmd == "jump"):
        if pe.can_jump():
          pe.jump(-8)
      elif(cmd == "stop_moving_left"):
        pe.set_movement(24,0)
      elif(cmd == "stop_moving_right"):
        pe.set_movement(-24,0)
  
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
  def __init__(self, name, host):
    super(GameController, self).__init__()
    
    self.name = name
    self.game = model.Game("foolevel")
    self.view = view.View(self.game)
    self.connection = Connection( (host, 18245) )
    self.connection.onRequest = self.incomingRequest
  
  def incomingRequest(self, req):
    msgName = req.properties.get('Message-Name')
    payload = demjson.decode(req.body)
    
    if(msgName == "entityChanged"):
      entity = self.game.level.entity_by_name(payload["name"])
      if entity is None:
        entity = self.game.level.create_entity(payload["name"])
        entView = view.SpriteView(entity, resources.get_sprite("samus"))
        entView.set_animation("stand")
        self.view.entity_views.append( entView )
        if len(self.game.level.entities) == 1:
          self.view.follow = self.game.level.entities[0]
      entity.pos.x = float(payload["pos"][0])
      entity.pos.y = float(payload["pos"][1])
    elif(msgName == "pleaseLogin"):
      print "I should log in"
      resp = req.response
      resp.properties['Message-Name'] = "login"
      resp.body = demjson.encode({"name": self.name})
      resp.send()
    
  
  def send(self, msgName, data):
    payload = demjson.encode(data)
    
    print "OMG sending ", msgName, data

    req = OutgoingRequest(self.connection, payload, {'Message-Name': msgName})
    req.compressed = True
    req.send()

  
  def action(self, what):
    self.send("player_action", {"action": what})
    
  def update(self, dt):
    asyncore.loop(timeout=0.01,count=1)
    
    self.view.update(dt)
    
  def draw(self):
    self.view.draw()