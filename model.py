# encoding: utf-8
"""
model.py

Created by Joachim Bengtsson on 2009-03-28.
Copyright (c) 2009 Third Cog Software. All rights reserved.
"""

import sys
import os
import euclid
import random
import physics
import pyglet
import resources
import math
from pyglet.gl import *
from boundingbox import *

import demjson

class GameDelegate:
  # parts is an array which contains any of: pos, state
  def entityChanged(self, entity, parts_that_changed):
    pass


class Player (object):
  def __init__(self):
    self.entity = None
    self.name = "Unnamed"
    self.connection = None
  
  def set_entity(self, Ent):
    self.entity = Ent
    self.entity.boundingbox = BoundingBox(euclid.Vector2(-self.entity.width/2, -self.entity.height), euclid.Vector2(self.entity.width/2, 0))
    Entity.physics_update = physics.forcebased_physics
  
  def update(self, dt):
    pass
  
class Game(object):
  """docstring for Game"""
  def __init__(self, level_name):
    super(Game, self).__init__()

    self.level = None
    self.players = []

    self.load_level(level_name)
    
    self.delegate = None
    
    self.gravity_force = euclid.Vector2(0,35.0)
    
  def load_level(self, name):  
    print "ladda level"
    
    self.level = Level(name)
    self.level.game = self
  
  def update(self, dt):
    self.level.update(dt)
    for p in self.players:
      p.update(dt)
  
  def gravity(self):
    return self.gravity_force
  
  def player_by_connection(self, conn):
    for p in self.players:
      if(p.connection == conn):
        return p
    p = Player()
    p.connection = conn
    self.players.append(p)
    return p

class Entity(object):
  """docstring for Entity"""
  def __init__(self, level, name, pos):
    super(Entity, self).__init__()
    self.level = None
    level.add_entity(self)
    self.pos = pos
    self.name = name
    self.vel = euclid.Vector2(0., 0.)
    self.acc = euclid.Vector2(0., 0.)

    self.move_force = euclid.Vector2(0,0)
    self.jump_force = euclid.Vector2(0,0)
    self.mass = 120
    self.max_vel = euclid.Vector2(7, 25)
    self.on_floor = False
    self.on_wall = False
    
    self.width = 0.75
    self.height = 2.5
    
    self.boundingbox = BoundingBox(euclid.Vector2(-self.width/2, -self.height/2), euclid.Vector2(self.width/2, self.height/2))
    
    self.view_direction = -1
    
    self.state = "running_left"
  
  def state():
      doc = "The state property."
      def fget(self):
          return self._state
      def fset(self, value):
          self._state = value
          if(self.level.game.delegate):
            self.level.game.delegate.entityChanged(self, ["state"])
          
      return locals()
  state = property(**state())
  
  
  def set_movement(self, x, y):
    self.move_force.x += x
    self.move_force.y += y
    
    if self.move_force.x == 0:
      self.vel.x = 0
  
  def set_mass(self, mass):
    self.mass = mass

  def can_jump(self):
    return self.on_floor
  
  def jump(self, amount):
    if self.view_direction < 0:
      self.state = 'jump_roll_right'
    else:
      self.state = 'jump_roll_left'
    self.jump_force.y = amount
    if amount != 0:
      self.vel.y -= 16
    elif self.vel.y < 0:
      self.vel.y = 0
  
  def update(self, tilemap, dt):
    if self.physics_update:
      self.physics_update(tilemap, dt)
    
    if self.state == 'jump_roll_left' or self.state == 'jump_roll_right':
      if self.on_floor:
        if self.view_direction < 0:
          self.state = 'running_left'
        else:
          self.state = 'running_right'
      else:
        if self.view_direction < 0:
          self.state = 'jump_roll_left'
        else:
          self.state = 'jump_roll_right'
    
    if(self.level.game.delegate):
      self.level.game.delegate.entityChanged(self, ["pos"])
    
  def collision(self, ent):
    if (self.pos - ent.pos).magnitude() < 1:
      print 'collision between %s and %s !!1!1!!!ONE' % (self.name, ent.name)
  
  def boundingbox(self):
    return self.bb

  def set_boundingbox(self, bb):
    self.bb = bb
    
  def boundingbox():
      doc = "The boundingbox property."
      def fget(self):
          return self._boundingbox
      def fset(self, value):
          self._boundingbox = value
      return locals()
  boundingbox = property(**boundingbox())

Entity.physics_update = physics.static_physics


    
    
    
class Level(object):
  """docstring for Level"""
  def __init__(self, name):
    super(Level, self).__init__()
    
    self.name = name
    
    self.entities = []
    self.game = None
  
    self.tilesets = [ resources.get_tileset("metroid") ]
    
    self.main_layer = self.load_main_layer()
    self.backgrounds = self.load_backgrounds()
    self.foregrounds = self.load_foregrounds()
      
  def add_entity(self, ent):
    ent.level = self
    self.entities.append(ent)
    
  def entity_by_name(self, name):
    for e in self.entities:
      if e.name == name:
        return e
    #e = Entity(self, name, euclid.Vector2(0,0))
    
    return None
    
  def create_entity(self, name):
    return Entity(self, name, euclid.Vector2(0,0))
    
  def update(self, dt):
    for ts in self.tilesets:
      ts.update(dt)
    
    # update entities
    for entity in self.entities:
      entity.update(self.main_layer.tilemap, dt)
      
    # check collisions
    for a in self.entities:
      for b in self.entities:
        if a == b:
          continue
        a.collision(b)
    
  def load_main_layer(self):
    layer_data_file = open("data/levels/" + self.name + "/main.layer")
    layer_data = demjson.decode(layer_data_file.read())
    
    return Layer(layer_data)    
    
  def load_backgrounds(self):    
    bg = open("data/levels/" + self.name + "/background.layers")
    bgdata = demjson.decode(bg.read())
    
    backs = []
    
    for b in bgdata:
      backs.append( Layer(b) )
      
    return backs
    
  def load_foregrounds(self):
    fg = open("data/levels/" + self.name + "/foreground.layers")
    fgdata = demjson.decode(fg.read())
    
    fores = []
    
    for f in fgdata:
      fores.append( Layer(f) )
      
    return fores  
    
  def gravity(self):
    return self.game.gravity()

class Color(object):
  """docstring for Color"""
  def __init__(self, r, g, b):
    super(Color, self).__init__()
    self.r = r
    self.g = g
    self.b = b
              
        
    
class Layer(object):
  """docstring for Layer"""
  def __init__(self, data):
    super(Layer, self).__init__()
        
    self.pos = euclid.Vector2(0.0, 0.0)    
    self.scroll = euclid.Vector2(data["scroll"][0], data["scroll"][1])
    self.color = Color(data["color"][0], data["color"][1], data["color"][2])
        
    self.tilemap = Tilemap(data["map"])   
    
        
class Tilemap(object):
  """docstring for Tilemap"""
  def __init__(self, data):
    super(Tilemap, self).__init__()
    
    self.map = data
    self.width = len(data[0])
    self.height = len(data)
  
  def tile_at_point(self, point):
    x = int(math.floor(point.x))
    y = int(math.floor(point.y))
    
    if x < 0 or y < 0 or x >= self.width or y >= self.height:
      return -1
      
    return self.map[y][x]
  
  def intersection(self, a, b):
    line = b - a
    dir = line.normalized()
    
    end = euclid.Vector2(b.x, b.y)
    end.x = math.floor(end.x)
    end.y = math.floor(end.y)
    
    point = euclid.Vector2(a.x, a.y)
    
    while True:
      x = int(math.floor(point.x))
      y = int(math.floor(point.y))
      if self.tile_at_point(euclid.Vector2(x,y)) != 0:
        return (x,y)
      point += dir
      if (x == end.x and y == end.y):
        break
    
    return None

  def __repr__(self):
    string = ''
    for row in self.map:
      string += str(row) + '\n'
    return string

    