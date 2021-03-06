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
    
    self.network = network.BestNetwork()
    self.network.startServer(name, 18245, self)
    
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
      player = self.game.find_or_create_player_by_connection(connection)

      action = payload["action"]
      
      self.logic.player_action(player, action)
    
    else:
      print "Unknown message:", payload
    
  
  def newConnection(self, conn):
    print "NEW CONNECTION ", conn
    player = self.game.find_or_create_player_by_connection(conn)
    
    self.network.send(conn, "pleaseLogin", {})
    
    print "please login"
    
  def lostConnection(self, conn, reason):
    print "A client got disconnected!",reason
    player = self.game.find_or_create_player_by_connection(conn)
    self.game.remove_player(player)
  
  def gotLogin(self, connection, payload):
    print "someone logged in"
    
    name = payload["name"]
    
    player = self.game.find_or_create_player_by_connection(connection)
    player.name = name
    
    self.playerChanged(player)
    
    for ent in self.game.level.entities:
      self.network.send(connection, "entityCreated", ent.rep("full"))
    
    self.logic.player_logged_in(player)
    
    
  def broadcast(self, msgName, payload):    
    for p in self.game.players:
      c = p.connection
      self.network.send(c, msgName, payload)
  
  def send(self, playerName, msgName, payload):
    pl = self.game.find_player_by_name(playerName)
    if not pl:
      raise "WTF, tried sending data to nonexistant player "+playerName
    
    self.network.send(pl.connection, msgName, payload)
      
      
  
  # Model delegates
  def entityChanged(self, entity, parts):
    self.broadcast("entityChanged", entity.rep(parts))
  
  def initEntity(self, entity, behavior = {}, physics = {}, **args):
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
  def play_sound(self, soundName, options = {}, onlyFor = None):
    payload = {"name":soundName, "options":options}
    if onlyFor == None:
      self.broadcast("playSound", payload)
    else:
      self.send(onlyFor, "playSound", payload)

  def stop_sound(self, soundID, onlyFor = None):
    payload = {"id": soundID}
    if onlyFor == None:
      self.broadcast("stopSound", payload)
    else:
      self.send(onlyFor, "stopSound", payload)
