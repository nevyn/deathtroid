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
  
class Game (object):
  pass

class Entity(object):
  """docstring for Entity"""
  def __init__(self, pos, vel, acc):
    super(Entity, self).__init__()
    self.pos = pos
    self.vel = vel
    self.acc = acc
    
  
class Level (object):
  pass

class Tilemap (object):
  pass
