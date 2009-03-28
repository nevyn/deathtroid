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
import math
from pyglet.gl import *
from boundingbox import *

import demjson

class GameDelegate:
  def entityChanged(self, entity):
    pass


class Player (object):
  def __init__(self):
    self.entity = None
    self.name = "Unnamed"
    self.connection = None
  
  def set_entity(self, Ent):
    self.entity = Ent
    self.entity.boundingbox = self.entity.player_boundingbox
    Entity.physics_update = physics.forcebased_physics
  
  def update(self, dt):
    if self.entity:
      # Reset jump-force
      self.entity.move_force.y = 0
  
class Game(object):
  """docstring for Game"""
  def __init__(self, level_name):
    super(Game, self).__init__()

    self.level = None
    self.players = []

    self.load_level(level_name)
    
    self.delegate = None
    
    self.gravity_force = euclid.Vector2(0,9.82)
    
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
    self.mass = 1
    self.max_vel = euclid.Vector2(7, 25)
    self.on_floor = False
    
    self.width = 1.0
    self.height = 2.0
  
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
    self.vel.y += amount
  
  def update(self, tilemap, dt):
    if self.physics_update:
      self.physics_update(tilemap, dt)
    
    if(self.level.game.delegate):
      self.level.game.delegate.entityChanged(self)
    
  def collision(self, ent):
    if (self.pos - ent.pos).magnitude() < 1:
      print 'collision between %s and %s !!1!1!!!ONE' % (self.name, ent.name)
  
  def boundingbox(self):
    return BoundingBox(euclid.Vector2(-self.width/2, -self.height), euclid.Vector2(self.width/2, 0))
    
    #return BoundingBox(euclid.Vector2(-self.width/2, -self.height/2), euclid.Vector2(self.width/2, self.height/2))

  def player_boundingbox(self):
    return BoundingBox(euclid.Vector2(-self.width/2, -self.height), euclid.Vector2(self.width/2, 0))

Entity.physics_update = physics.static_physics

    
    
  
    
    
    
class Level(object):
  """docstring for Level"""
  def __init__(self, name):
    super(Level, self).__init__()
    
    self.name = name
    
    self.entities = []
    self.game = None
  
    self.tilemap = self.load_tilemap()
    
    self.tilesets = [Tileset("metroid")]
      
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
    # update entities
    for entity in self.entities:
      entity.update(self.tilemap, dt)
      
    # check collisions
    for a in self.entities:
      for b in self.entities:
        if a == b:
          continue
        a.collision(b)
    
  def load_tilemap(self):

    try:
      tm = open("data/levels/" + self.name + "/tilemap.data")
    except:
      print "Fuck you!"
      raise
      
    return Tilemap(demjson.decode(tm.read()))    
        
class Tilemap(object):
  """docstring for Tilemap"""
  def __init__(self, tilemap):
    super(Tilemap, self).__init__()
    
    self.map = tilemap
    self.width = len(tilemap[0])
    self.height = len(tilemap)
  
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
        return True
      point += dir
      if (x == end.x and y == end.y):
        break
    
    return False

  def __repr__(self):
    string = ''
    for row in self.map:
      string += str(row) + '\n'
    return string

class Tileset(object):
  """docstring for Tileset"""
  def __init__(self, name):
    super(Tileset, self).__init__()
    
    # load definition file
    
    # load actual texture
    
    # calculate coords

    self.image = pyglet.image.load("data/tilesets/" + name + ".png")
    seq = pyglet.image.ImageGrid(self.image, 1, 16)
    self.tiles = pyglet.image.TextureGrid(seq)
    #self.tiles = pyglet.image.Texture3D.create_for_image_grid(seq)
    
    print "target: ", self.tiles.target
    print "id: ", self.tiles.id
    
    glBindTexture(GL_TEXTURE_2D, self.tiles.id)
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        
    print self.tiles
    