# encoding: utf-8

import euclid
import random
import uuid

import physics
import model
from boundingbox import *
from pyglet import clock

class LogicDelegate:
  def play_sound(self, soundName, options):
    pass
    
  def stop_sound(self, soundID):
    pass

class Logic(object):
  """Logic handler; what to do with player input, collisions, etc"""
  def __init__(self, game, delegate):
    super(Logic, self).__init__()
    self.game = game
    self.delegate = delegate
    
  def collision(self, a, b, point):

    if a:
      a.behavior.collided(b)
    if b:
      b.behavior.collided(a)

  def player_action(self, player, action):
    pe = player.entity
    
    if not pe:
      if action == "fire":
        self.spawn_player(player)
      return
    
    if(action == "move_left"):
      pe.set_movement(-24,0)
      pe.add_state("run")
      pe.add_state("view_left")
      pe.view_direction = -1
    elif(action == "move_right"):
      pe.set_movement(24,0)
      pe.add_state("run")
      pe.add_state("view_right")
      pe.view_direction = 1
    elif(action == "jump"):
      if pe.behavior.can_jump():
        pe.behavior.jump(-2500)
    
    elif(action == "stop_moving_left"):
      pe.set_movement(24,0)
      pe.remove_state("view_left")
      if pe.move_force.x == 0:
        pe.remove_state("run")
    elif(action == "stop_moving_right"):
      pe.set_movement(-24,0)
      pe.remove_state("view_right")
      if pe.move_force.x == 0:
        pe.remove_state("run")
    elif(action == "stop_jump"):
      pe.behavior.jump(0)
      
    elif(action == "fire"):
      pe.behavior.fire()
  
  def player_logged_in(self, player):
    self.spawn_player(player)
  
  def play_sound(self, soundName, options = {}):
    self.delegate.play_sound(soundName, options)
    
  def stop_sound(self, soundID):
    self.delegate.stop_sound(soundID)
  
  def spawn_player(self, player):
    E = model.Entity(self.game.level, "samus", "player "+player.name, euclid.Vector2(random.randint(1, 10),3))
    E.player = player
    player.set_entity(E)
  
  def initializeEntity(self, entity, **args):
    from . import behaviors, avatar
    behaviors = {
      "avatar": avatar.AvatarBehavior,
      "projectile": behaviors.ProjectileBehavior,
      "explosion": behaviors.ExplosionBehavior
    }
    if entity.behaviorName in behaviors:
      entity.behavior = behaviors[entity.behaviorName](entity, self, **args)

class Behavior(object):
  """Base class for all behaviors"""
  def __init__(self, entity, logic):
    super(Behavior, self).__init__()
    self.entity = entity
    self.logic = logic
  
  def update(self, dt):
    pass
  
  def collided(self, other):
    pass
    
  def play_sound(self, name, opts = {}):
    opts["position"] = [self.entity.pos.x, self.entity.pos.y]
    self.logic.play_sound(name, opts)

__all__ = ['behaviors']