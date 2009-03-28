#!/usr/bin/env python
# encoding: utf-8
"""
model.py

Created by Joachim Bengtsson on 2009-03-28.
Copyright (c) 2009 Third Cog Software. All rights reserved.
"""

import sys
import os

class Player (object):
  pass
  
class Game(object):
  """docstring for Game"""
  def __init__(self, level_name):
    super(Game, self).__init__()

    self.load_level(level_name)
    
  def load_level(self, name):
    
    pass    
    
      

class Entity(object):
  """docstring for Entity"""
  def __init__(self, pos):
    super(Entity, self).__init__()
    self.pos = pos
    self.vel = euclid.Vector2(0., 0.)
    self.acc = euclid.Vector2(0., 0.)
    
class Level(object):
  """docstring for Level"""
  def __init__(self):
    super(Level, self).__init__()
    
    self.entities = []
    
  def load_tilemap(self, name):
    pass
    
    
class Tilemap(object):
  """docstring for Tilemap"""
  def __init__(self, width, height):
    super(Tilemap, self).__init__()
    
    self.tilemap = [[0 for x in range(width)] for y in range(height)]