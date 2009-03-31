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

# This is taken from itertools from python2.6
def combinations(iterable, r):
    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    # combinations(range(4), 3) --> 012 013 023 123
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = range(r)
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i+1, r):
            indices[j] = indices[j-1] + 1
        yield tuple(pool[i] for i in indices)

class GameDelegate:
  # parts is an array which contains any of: pos, state
  def entityChanged(self, entity, parts_that_changed):
    pass
  
  def entityCreated(self, entity):
    pass
  
  def entitiesCollidedAt(self, entity1, entity2, point):
    pass
  
  def playerChanged(self, player):
    pass

class Player (object):
  def __init__(self):
    self.entity = None
    self.name = "Unnamed"
    self.connection = None
    self._score = 0
  
  def set_entity(self, Ent):
    self.entity = Ent
    if not Ent:
      return
    self.entity.boundingbox = BoundingBox(euclid.Vector2(-self.entity.width/2, -self.entity.height), euclid.Vector2(self.entity.width/2, 0))
    self.entity.physics_update = physics.forcebased_physics
  
  def update(self, dt):
    pass
    
  def score():
      doc = "The score property."
      def fget(self):
          return self._score
      def fset(self, value):
          self._score = value
          if self.game.delegate:
            self.game.delegate.scoreChangedForPlayer(self)
            self.game.delegate.playerChanged(self)
      def fdel(self):
          del self._score
      return locals()
  score = property(**score())
  
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
    p.game = self
    self.players.append(p)
    return p
    
  def is_on_server():
    return self.delegate != None

class Entity(object):
  """An entity in the game world.
  - Type is the exact type of the entity, and will be used to deduce which sprite and visual representation to use
  - Behavior is used to lookup logics behavior for the entity
  - Name must be unique (or None if it'll be set in the delegate's entityCreated).
  - Pos is an euclid.Vector2
  """
  def __init__(self, level, type_, behaviorName, physicsName, name, pos, width, height, *behaviorArgs):
    super(Entity, self).__init__()
    self.level = None # Set by level.add_entity
    level.add_entity(self)
    self.pos = pos
    self.type = type_
    self.behaviorName = behaviorName
    self.physicsName = physicsName
    self.name = name
    self.vel = euclid.Vector2(0., 0.)
    self.acc = euclid.Vector2(0., 0.)

    self.mass = 120
    self.max_vel = euclid.Vector2(7, 25)
    self.physics_update = physics.static_physics
    
    self.width = width
    self.height = height
    
    self._boundingbox = BoundingBox(euclid.Vector2(-self.width/2, -self.height/2), euclid.Vector2(self.width/2, self.height/2))
    
    self.view_direction = 1
    
    self._state = []
    
    if self.level.game.delegate:
      self.level.game.delegate.initEntity(self, behaviorArgs)
      self.level.game.delegate.entityCreated(self)
  
  def remove(self):
    if self.level.game.delegate:
      self.level.game.delegate.entityRemoved(self)
    
    self.level.remove_entity(self)
  
  def state():
      doc = "The state property."
      def fget(self):
          return self._state
      def fset(self, value):
          if not isinstance(value, list):
            raise "old style state forbidden, use {add,remove}_state instead"
          
          self._state = value
          if(self.level.game.delegate):
            self.level.game.delegate.entityChanged(self, ["state"])
          
      return locals()
  state = property(**state())
  
  def add_state(self, state):
    if not state in self.state:
      self.state = self.state + [state]
  
  def remove_state(self, state):
    if state in self._state:
      self._state.remove(state)
    self.state = self._state
  
  def set_movement(self, x, y):
    self.move_force.x += x
    self.move_force.y += y
    
    if self.move_force.x == 0:
      self.vel.x = 0
  
  def set_mass(self, mass):
    self.mass = mass
    
  def update(self, tilemap, dt):
    if self.physics_update:
      self.physics_update(self, tilemap, dt)
    
    if "jump" in self.state:
      if self.on_floor:
        self.remove_state("jump")
    
    if(self.level.game.delegate):
      self.level.game.delegate.entityChanged(self, ["pos"])

  def boundingbox():
      doc = "The boundingbox property."
      def fget(self):
          return self._boundingbox
      def fset(self, value):
          self._boundingbox = value
          if(self.level.game.delegate):
            self.level.game.delegate.entityChanged(self, ["boundingbox"])
          
      return locals()
  boundingbox = property(**boundingbox())
  
  @staticmethod
  def from_rep(rep, inLevel):
    w = float(rep["size"][0])
    h = float(rep["size"][1])
    x = float(rep["pos"][0])
    y = float(rep["pos"][1])
    entity = Entity(inLevel, rep["type"], rep["behaviorName"], rep["physicsName"], rep["name"], euclid.Vector2(x, y), w, h)
    entity.update_from_rep(rep)
    return entity
  
  
  def rep(self, parts = "full"):
    rep = {
      "name": self.name
    }
    if parts is "full":
      rep["type"] = self.type
      rep["behaviorName"] = self.behaviorName
      rep["physicsName"] = self.physicsName
      
    if parts is "full" or "boundingbox" in parts:
      rep["boundingbox"] = [self.boundingbox.min.x, self.boundingbox.min.y, self.boundingbox.max.x, self.boundingbox.max.y]
    
    if parts is "full" or "size" in parts:
      rep["size"] = [self.width, self.height]
      
    if parts is "full" or "pos" in parts:
      rep["pos"] = [self.pos.x, self.pos.y]
    
    if parts is "full" or "state" in parts:
      rep["state"] = self.state
      
    return rep
  
  def update_from_rep(self, rep):
    if "pos" in rep:
      self.pos.x = float(rep["pos"][0])
      self.pos.y = float(rep["pos"][1])
    if "boundingbox" in rep:
      self.boundingbox.min.x = float(rep["boundingbox"][0])
      self.boundingbox.min.y = float(rep["boundingbox"][1])
      self.boundingbox.max.x = float(rep["boundingbox"][2])
      self.boundingbox.max.y = float(rep["boundingbox"][3])
    
    if "state" in rep:
      self.state = rep["state"]
    
    
    
class Level(object):
  """docstring for Level"""
  def __init__(self, name):
    super(Level, self).__init__()
    
    self.name = name
    
    self.entities = []
    self.game = None
  
    #self.tilesets = [ resources.get_tileset("metroid") ]
    
    self.main_layer = self.load_main_layer()
    self.backgrounds = self.load_backgrounds()
    self.foregrounds = self.load_foregrounds()
      
  def add_entity(self, ent):
    ent.level = self
    self.entities.append(ent)
  
  def remove_entity(self, ent):
    self.entities.remove(ent)
    
  def entity_by_name(self, name):
    for e in self.entities:
      if e.name == name:
        return e
    
    return None
        
  def update(self, dt):
    resources.update(dt)
          
    # update entities
    for entity in self.entities:
      entity.update(self.main_layer.tilemap, dt)
      
    # check collisions
    for a, b in combinations(self.entities, 2) :
      if physics.is_colliding(a, b):
        print a.name, 'collides with', b.name
        self.game.delegate.entitiesCollidedAt(a, b, a.pos)
        
    
  def load_main_layer(self):
    layer_data_file = open("data/levels/" + self.name + "/main.layer")
    layer_data = demjson.decode(layer_data_file.read())
    
    return Layer(layer_data, "main")    
    
  def load_backgrounds(self):    
    bg = open("data/levels/" + self.name + "/background.layers")
    bgdata = demjson.decode(bg.read())
    
    backs = []
    
    for b in bgdata:
      backs.append( Layer(b, "BG_" + str(len(bgdata))) )
      
    return backs
    
  def load_foregrounds(self):
    fg = open("data/levels/" + self.name + "/foreground.layers")
    fgdata = demjson.decode(fg.read())
    
    fores = []
    
    for f in fgdata:
      fores.append( Layer(f, "FG_" + str(len(fgdata))) )
      
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
  def __init__(self, data, name):
    super(Layer, self).__init__()
    
    self.name = name
    
    self.startpos = euclid.Vector2(0.0, 0.0)
        
    self.offset = euclid.Vector2(0.0, 0.0)
    self.scroll = euclid.Vector2(data["scroll"][0], data["scroll"][1])
    self.color = Color(data["color"][0], data["color"][1], data["color"][2])
    
    tilesetname = data["tileset"]
    self.tileset = resources.get_tileset(tilesetname)
    
    if "auto" in data:
      self.auto = euclid.Vector2(data["auto"][0], data["auto"][1])
    else:
      self.auto = euclid.Vector2(0.0, 0.0)
      
    if "repeat" in data:
      self.repeatx = data["repeat"][0]
      self.repeaty = data["repeat"][1]
    else:
      self.repeatx = self.repeaty = False
      
    if "position" in data:
      self.startpos.x = data["position"][0]
      self.startpos.y = data["position"][1]
        
    self.tilemap = Tilemap(data["map"])
    
  def update(self, dt):
    self.offset += self.auto * dt
    
    if self.offset.x >= self.tilemap.width:
      self.offset.x = int(self.offset.x - self.tilemap.width)
    elif self.offset.x < -self.tilemap.width:
      self.offset.x = int(self.offset.x - -self.tilemap.width)
      
    if self.offset.y >= self.tilemap.height:
      self.offset.y = int(self.offset.y - self.tilemap.height)
    elif self.offset.y < -self.tilemap.height:
      self.offset.y = int(self.offset.y - -self.tilemap.height)
    
        
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

    