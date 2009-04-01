# encoding: utf-8

import euclid
import random

import physics
import model

class Logic(object):
  """Logic handler; what to do with player input, collisions, etc"""
  def __init__(self, game):
    super(Logic, self).__init__()
    self.game = game
    
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
  
  def spawn_player(self, player):
    E = model.Entity(self.game.level, "samus", "avatar", "force", "player "+player.name, euclid.Vector2(random.randint(1, 10),3), 0.75, 2.5, physics={'mass': 120})
    E.player = player
    player.set_entity(E)
  
  def initializeEntity(self, entity, **args):
    behaviors = {
      "avatar": AvatarBehavior,
      "projectile": ProjectileBehavior
    }
    if entity.behaviorName in behaviors:
      entity.behavior = behaviors[entity.behaviorName](entity, **args)

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
    self.health = 100
    
  def fire(self):
    pe = self.entity
    projectile = model.Entity(pe.level, "bullet1", "projectile", "projectile", None, euclid.Vector2(pe.pos.x, pe.pos.y - 1.8), 0.5, 0.5, behavior={'firingEntity': pe})
  
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
  
  def collided(self, other):
    if other and other.behaviorName == "projectile" and other.behavior.firingEntity != self.entity:
      self.health -= 10
      print "Health", self.health
      if self.health <= 0:
        other.behavior.firingEntity.player.score += 1
        self.die()
  
  def die(self):
    self.entity.player.set_entity(None)
    self.entity.remove()
  
class ProjectileBehavior(Behavior):
  """Behavior for anything fired from a gun."""
  def __init__(self, entity, firingEntity):
    super(ProjectileBehavior, self).__init__(entity)
    entity.vel = firingEntity.view_direction*euclid.Vector2(20, 0)
    entity.name = next_projectile_name()
    
    self.firingEntity = firingEntity
    
    entity.state = ["r"]
  
  def collided(self, other):
    if not other or (other != self.firingEntity and other.behaviorName != "projectile"):
      self.entity.remove()
    

projectile_id = 0
def next_projectile_name():
  global projectile_id
  projectile_id += 1
  return "projectile "+str(projectile_id)
