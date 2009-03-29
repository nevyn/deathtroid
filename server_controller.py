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
import view
import euclid
import random
import asyncore

import resources
import network
  

class ServerController(object):
  """docstring for ServerController"""
  def __init__(self):
    print "Starting server"
    super(ServerController, self).__init__()
    
    self.game = model.Game("foolevel")
    self.game.delegate = self
    
    network.startServer(18245, self)
    
    print "Server is running"
      
  def update(self, dt):
    self.game.update(dt)
  
  def close(self):
    pass
  
  # Network
  
  def gotData(self, connection, msgName, payload):
    if msgName == "login":
      self.gotLogin(connection, payload)
    elif msgName == "player_action":
      player = self.game.player_by_connection(connection)

      pe = player.entity

      cmd = payload["action"]
      if(cmd == "move_left"):
        pe.set_movement(-24,0)
        if pe.state != "jump_roll_right" and pe.state != "jump_roll_left":
          pe.state = "running_left"
        pe.view_direction = -1
      elif(cmd == "move_right"):
        pe.set_movement(24,0)
        if pe.state != "jump_roll_right" and pe.state != "jump_roll_left":
          pe.state = "running_right"
        pe.view_direction = 1
      elif(cmd == "jump"):
        if pe.can_jump():
          pe.jump(-2500)
      elif(cmd == "stop_moving_left"):
        pe.set_movement(24,0)
        pe.state = "stand_left"
      elif(cmd == "stop_moving_right"):
        pe.set_movement(-24,0)
        pe.state = "stand_right"
      elif(cmd == "stop_jump"):
        pe.jump(0)
        
      elif(cmd == "fire"):
        pe.fire()
    
    else:
      print "Unknown message:", payload
    
  
  def newConnection(self, conn):
    print "NEW CONNECTION ", conn
    player = self.game.player_by_connection(conn)
    
    network.send(conn, "pleaseLogin", {})
    
    print "please login"
  
  def gotLogin(self, connection, payload):
    print "someone logged in"
    
    name = payload["name"]
    
    player = self.game.player_by_connection(connection)
    player.name = name
    
    self.playerChanged(player)
    
    for ent in self.game.level.entities:
      network.send(connection, "entityCreated", ent.rep("full"))
    
    E = model.Entity(self.game.level, "samus", "player "+name, euclid.Vector2(random.randint(1, 10),3), 0.75, 2.5)
    player.set_entity(E)
    
  def broadcast(self, msgName, data):    
    for p in self.game.players:
      c = p.connection
      network.send(c, msgName, data)
      
  
  # Model delegates
  def entityChanged(self, entity, parts):
    self.broadcast("entityChanged", entity.rep(parts))
  
  def entityCreated(self, entity):
    self.broadcast("entityCreated", entity.rep("full"))
    
  def entityRemoved(self, entity):
    self.broadcast("entityRemoved", entity.name)
    
  def playerChanged(self, player):
    pass
    
