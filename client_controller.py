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
from twisted.internet.protocol import Protocol, ClientFactory
import pygletreactor
pygletreactor.install() # <- this must come before...
from twisted.internet import reactor, task # <- ...importing this reactor!

import resources


from twisted.internet.protocol import ClientCreator

from network import *


class DeathtroidFactory (ClientFactory):
  
  protocol = DeathtroidProtocol
  
  def __init__(self, controller):
    self.controller = controller
  
  def buildProtocol(self, addr):
    newProto = ClientFactory.buildProtocol(self, addr)
    newProto.controller = self.controller
    return newProto


class ClientController(object):
  """hej"""
  def __init__(self, name, host):
    print "Starting client"
    super(ClientController, self).__init__()
    
    self.name = name
    self.game = model.Game("foolevel")
    self.view = view.View(self.game)
    
    
    reactor.connectTCP(host, 18245, DeathtroidFactory(self))
    
    self.entityViews = []
    
    print "Client is running"
  
  def newConnection(self, conn):
    self.connection = conn
    print "Got client connection"
  
  def gotData(self, connection, data):
    msgName = data['Message-Name']
    payload = data['Payload']
    
    if(msgName == "entityChanged"):
      print "Entity updated", payload
      entity = self.game.level.entity_by_name(payload["name"])
      if entity is None:
        entity = self.game.level.create_entity(payload["name"])
        entView = view.SpriteView(entity, resources.get_sprite("samus"))
        entView.set_animation("run_left")
        self.view.entity_views.append( entView )
        if len(self.game.level.entities) == 1:
          self.view.follow = self.game.level.entities[0]
        
      entity.pos.x = float(payload["pos"][0])
      entity.pos.y = float(payload["pos"][1])
      entity.state = payload["state"]
      
    elif(msgName == "pleaseLogin"):
      print "I should log in"
      connection.send("login", {"name": self.name})
    
  
  def send(self, msgName, data):
    
    print "OMG sending ", msgName, data
    self.connection.send(msgName, data)

  
  def action(self, what):
    self.send("player_action", {"action": what})
    
  def update(self, dt):
    self.view.update(dt)
  
  def draw(self):
    self.view.draw()    
