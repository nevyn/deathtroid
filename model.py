#!/usr/bin/env python
# encoding: utf-8
"""
model.py

Created by Joachim Bengtsson on 2009-03-28.
Copyright (c) 2009 Third Cog Software. All rights reserved.
"""

import sys
import os
import euclid

class Player (object):
  def __init(self):
    self.entity = None
  
  def set_entity(self, Ent):
    self.entity = Ent
  
class Game(object):
  """docstring for Game"""
  def __init__(self, level_name):
    super(Game, self).__init__()

    self.load_level(level_name)

    P = Player()
    E = Entity(self.level, euclid.Vector2(0,0))
    P.set_entity(E)
    self.player = [P]
    
  def load_level(self, name):
    self.level = Level()
    pass
  
  def update(self, dt):
    self.level.update(dt)

class Entity(object):
  """docstring for Entity"""
  def __init__(self, level, pos):
    super(Entity, self).__init__()
    level.add_entity(self)
    self.pos = pos
    self.vel = euclid.Vector2(0., 0.)
    self.acc = euclid.Vector2(0., 0.)

  def update(self, dt):
    self.pos += self.vel
    self.vel += self.acc
    
class Level(object):
  """docstring for Level"""
  def __init__(self):
    super(Level, self).__init__()
    
    self.entities = []
  
  def add_entity(self, ent):
    self.entities.append(ent)
  
  def load_tilemap(self, name):
    pass
  
  def update(self, dt):
    for entity in self.entities:
      entity.update(dt)
    
    
class Tilemap(object):
  """docstring for Tilemap"""
  def __init__(self, width, height):
    super(Tilemap, self).__init__()
    
    self.tilemap = [[0 for x in range(width)] for y in range(height)]