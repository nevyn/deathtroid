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
import datetime
import asyncore

import resources

import network


class ClientController(object):
  """hej"""
  def __init__(self, name, host):
    print "Starting client"
    super(ClientController, self).__init__()
    
    self.name = name
    self.game = model.Game("foolevel")
    self.view = view.View(self.game)
    self.t = datetime.datetime.now()
    
    network.startClient(host, 18245, self)
    
    self.entityViews = []
    
    print "Client is running"
  
  def newConnection(self, conn):
    self.connection = conn
    print "Got client connection"
  
  def gotData(self, connection, msgName, payload):
    
    if(msgName == "entityChanged"):
      
      print "Entity updated", payload
      t = datetime.datetime.now()
      print 'dt:', t - self.t
      self.t = t
      
      entity = self.game.level.entity_by_name(payload["name"])
      if entity is None:
        entity = self.game.level.create_entity(payload["name"])
        entView = view.SpriteView(entity, resources.get_sprite("samus"))
        entView.set_animation("run_left")
        self.view.level_view.entity_views.append( entView )
        if entity.name == "player "+self.name:
          self.view.follow = entity
        
      entity.pos.x = float(payload["pos"][0])
      entity.pos.y = float(payload["pos"][1])
      entity.state = payload["state"]
      
    elif(msgName == "pleaseLogin"):
      print "I should log in"
      self.send("login", {"name": self.name})
    
  
  def send(self, msgName, data):
    network.send(self.connection, msgName, data)

  
  def action(self, what):
    self.send("player_action", {"action": what})
    
  def update(self, dt):
    self.view.update(dt)
    asyncore.loop(timeout=0.01,count=1)
  
  def draw(self):
    self.view.draw()    
