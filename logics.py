# encoding: utf-8

import euclid
import random
import uuid

import physics
import model
from boundingbox import *

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
    behaviors = {
      "avatar": AvatarBehavior,
      "projectile": ProjectileBehavior
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


def volumeIncreaseCallback(voice):
  if voice.volume < 0.3:
    voice.volume += 0.01


class AvatarBehavior(Behavior):
  """Behavior for an entity that represents a player in-game"""
  def __init__(self, entity, logic, jump_width, jump_height, **args):
    super(AvatarBehavior, self).__init__(entity, logic)
    entity.move_force = euclid.Vector2(0,0)
    entity.jump_force = euclid.Vector2(0,0)
    entity.on_floor = False
    entity.on_wall = False
    entity.state = ["view_right"]
    
    self.normal_bb = BoundingBox(euclid.Vector2(-entity.width/2, -entity.height), euclid.Vector2(entity.width/2, 0))
    self.jump_bb = BoundingBox(euclid.Vector2(-jump_width/2, -jump_height/2-entity.height/2), euclid.Vector2(jump_width/2, jump_height/2-entity.height/2))
    entity.boundingbox = self.normal_bb
    
    self.was_in_air = True
    
    self.health = 100
    
  def fire(self):
    pe = self.entity
    projectile = model.Entity(pe.level, "bullet1", None, euclid.Vector2(pe.pos.x, pe.pos.y - 1.8), behavior={'firingEntity': pe})
    self.logic.play_sound("BaseShot", {"position": [pe.pos.x, pe.pos.y]})
  
  def can_jump(self):
    return self.entity.on_floor
  
  def jump(self, amount):
    pe = self.entity
    pe.jump_force.y = amount
    if amount != 0:
      self.entity.boundingbox = self.jump_bb
      pe.add_state("jump")
      
      self.spinSoundID = uuid.uuid4().hex
      self.logic.play_sound("Spin", {"follow": pe.name, "id":  self.spinSoundID, "loop": True, "callback": volumeIncreaseCallback, "volume": 0.05})
      
      pe.vel.y -= 16
    elif pe.vel.y < 0:
      pe.vel.y = 0
  
  def update(self, dt):
    if self.was_in_air and self.entity.on_floor:
      self.on_landing()
        
    self.was_in_air = not self.entity.on_floor
  
  def on_landing(self):
    if "jump" in self.entity.state:
      self.entity.boundingbox = self.normal_bb
      self.entity.remove_state("jump")
      self.logic.stop_sound(self.spinSoundID)
    self.logic.play_sound("Land", {"position": [self.entity.pos.x, self.entity.pos.y]})
  
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
  def __init__(self, entity, logic, firingEntity, **args):
    super(ProjectileBehavior, self).__init__(entity, logic)
    entity.vel = firingEntity.view_direction*euclid.Vector2(20, 0)
    entity.name = next_projectile_name()
    
    self.firingEntity = firingEntity
    
    print "view direction", firingEntity.view_direction
    
    if firingEntity.view_direction == 1:
      entity.state = ["r"]
    else:
      entity.state = ["l"]
  
  def collided(self, other):
    if not other or (other != self.firingEntity and other.behaviorName != "projectile"):
      self.entity.remove()
      self.logic.play_sound("Burst", {"position": [self.entity.pos.x, self.entity.pos.y]})
    

projectile_id = 0
def next_projectile_name():
  global projectile_id
  projectile_id += 1
  return "projectile "+str(projectile_id)
