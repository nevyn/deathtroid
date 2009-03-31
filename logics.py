# encoding: utf-8

import euclid
import random

import physics
import model

class Logic(object):
  """Logic handler; what to do with player input, collisions, etc"""
  def __init__(self):
    super(Logic, self).__init__()
    
  def collision(self, a, b, point):
    if a:
      a.behavior.collided(b)
    if b:
      b.behavior.collided(a)

  def player_action(self, player, action):
    pe = player.entity
    
    if(action == "move_left"):
      pe.set_movement(-24,0)
      pe.add_state("run")
      pe.add_state("view_left")
      pe.remove_state("view_right")
      pe.view_direction = -1
    elif(action == "move_right"):
      pe.set_movement(24,0)
      pe.add_state("run")
      pe.add_state("view_right")
      pe.remove_state("view_left")
      pe.view_direction = 1
    elif(action == "jump"):
      if pe.behavior.can_jump():
        pe.behavior.jump(-2500)
    
    elif(action == "stop_moving_left"):
      pe.set_movement(24,0)
      pe.remove_state("run")
    elif(action == "stop_moving_right"):
      pe.set_movement(-24,0)
      pe.remove_state("run")
    elif(action == "stop_jump"):
      pe.behavior.jump(0)
      
    elif(action == "fire"):
      pe.behavior.fire()
  
  def player_logged_in(self, player, to_game):
    E = model.Entity(to_game.level, "samus", "avatar", "player "+player.name, euclid.Vector2(random.randint(1, 10),3), 0.75, 2.5)
    player.set_entity(E)
    
  
  def initializeEntity(self, entity, args):
    behaviors = {
      "avatar": AvatarBehavior,
      "projectile": ProjectileBehavior
    }
    if entity.behaviorName in behaviors:
      entity.behavior = behaviors[entity.behaviorName](entity, *args)

class Behavior(object):
  """Base class for all behaviors"""
  def __init__(self, entity):
    super(Behavior, self).__init__()
    self.entity = entity
  
  def collided(self, other):
    pass
    

class AvatarBehavior(Behavior):
  """Behavior for an entity that represents a player in-game"""
  def __init__(self, entity):
    super(AvatarBehavior, self).__init__(entity)
    entity.move_force = euclid.Vector2(0,0)
    entity.jump_force = euclid.Vector2(0,0)
    entity.on_floor = False
    entity.on_wall = False
    entity.state = ["view_right"]
    
  def fire(self):
    pe = self.entity
    projectile = model.Entity(pe.level, "bullet1", "projectile", None, euclid.Vector2(pe.pos.x, pe.pos.y - 1.8), 0.5, 0.5, pe)
  
  def can_jump(self):
    return self.entity.on_floor
  
  def jump(self, amount):
    pe = self.entity
    pe.jump_force.y = amount
    if amount != 0:
      pe.add_state("jump")
      pe.vel.y -= 16
    elif pe.vel.y < 0:
      pe.remove_state("jump")
      pe.vel.y = 0

class ProjectileBehavior(Behavior):
  """Behavior for anything fired from a gun."""
  def __init__(self, entity, firingAvatar):
    super(ProjectileBehavior, self).__init__(entity)
    entity.physics_update = physics.projectile_physics
    entity.vel = firingAvatar.view_direction*euclid.Vector2(10, 0)
    entity.name = next_projectile_name()
    
    entity.state = ["r"]
  
  def collided(self, other):
    self.entity.remove()
    

projectile_id = 0
def next_projectile_name():
  global projectile_id
  projectile_id += 1
  return "projectile "+str(projectile_id)
