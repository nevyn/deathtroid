# encoding: utf-8
"""
controller.py

Created by Joachim Bengtsson on 2009-03-28.
Copyright (c) 2009 Third Cog Software. All rights reserved.
"""

import sys
import os
import demjson
import euclid
import random
import asyncore

import view
import model
import resources
import network
import logics
import physics

class ServerController(object):
  """docstring for ServerController"""
  def __init__(self, name):
    print "Starting server", name
    super(ServerController, self).__init__()
    
    self.name = name
    self.game = model.Game("foolevel")
    self.game.delegate = self
    
    self.logic = logics.Logic(self.game, self) # todo: DeathmatchLogic() or something
    self.physics = physics.Physics(self.game)
    
    network.startServer(name, 18245, self)
    
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

      action = payload["action"]
      
      self.logic.player_action(player, action)
    
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
    
    self.logic.player_logged_in(player)
    
    
  def broadcast(self, msgName, data):    
    for p in self.game.players:
      c = p.connection
      network.send(c, msgName, data)
      
  
  # Model delegates
  def entityChanged(self, entity, parts):
    self.broadcast("entityChanged", entity.rep(parts))
  
  def initEntity(self, entity, behavior = {}, physics = {}, **args):
    print 'initentity', behavior, physics, args
    self.logic.initializeEntity(entity, **behavior)
    self.physics.initializeEntity(entity, **physics)
  
  def entityCreated(self, entity):
    #todo: if the ent is an avatar for the player we're sending this msg to, append "this is you" to the dict, so that the client doesn't have to rely on the entity name to locate itself. might also use owner=playerID, and sync players to the client
    self.broadcast("entityCreated", entity.rep("full"))
    
  def entityRemoved(self, entity):
    self.broadcast("entityRemoved", entity.name)
    
  def playerChanged(self, player):
    pass
    
  def scoreChangedForPlayer(self, player):
    print "    \n\n"
    print "    Score board:"
    print "    ------------"
    for p in self.game.players:
      print "     ", p.name, ": ", p.score
    print "\n\n"
    
  def entitiesCollidedAt(self, entA, entB, point):
    self.logic.collision(entA, entB, point)
  
  # Logic delegates
  def play_sound_at(self, soundName, position):
    self.broadcast("playSound", {"name":soundName, "position":[position.x, position.y]})

