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
    (x,y) = point
    print 'collition between %s and %s at tile %dx%d' % (a,b,x,y)
    a.vel.x = 0
    a.vel.y = 0
    a.remove()

  def player_action(self, player, action):
    pe = player.entity
    
    if(action == "move_left"):
      pe.set_movement(-24,0)
      if pe.state != "jump_roll_right" and pe.state != "jump_roll_left":
        pe.state = "running_left"
      pe.view_direction = -1
    elif(action == "move_right"):
      pe.set_movement(24,0)
      if pe.state != "jump_roll_right" and pe.state != "jump_roll_left":
        pe.state = "running_right"
      pe.view_direction = 1
    elif(action == "jump"):
      if pe.behaviorHelper.can_jump():
        pe.behaviorHelper.jump(-2500)
    
    elif(action == "stop_moving_left"):
      pe.set_movement(24,0)
      pe.state = "stand_left"
    elif(action == "stop_moving_right"):
      pe.set_movement(-24,0)
      pe.state = "stand_right"
    elif(action == "stop_jump"):
      pe.behaviorHelper.jump(0)
      
    elif(action == "fire"):
      pe.behaviorHelper.fire()
  
  def player_logged_in(self, player, to_game):
    E = model.Entity(to_game.level, "samus", "avatar", "player "+player.name, euclid.Vector2(random.randint(1, 10),3), 0.75, 2.5)
    player.set_entity(E)
    
  
  def initializeEntity(self, entity):
    behaviors = {
      "avatar": AvatarBehavior
    }
    if entity.behavior in behaviors:
      entity.behaviorHelper = behaviors[entity.behavior](entity)

class AvatarBehavior(object):
  """Behavior for an entity that represents a player in-game"""
  def __init__(self, entity):
    super(AvatarBehavior, self).__init__()
    self.entity = entity
    
  def fire(self):
    pe = self.entity
    projectile = model.Entity(pe.level, "shot", "projectile", next_projectile_name(), euclid.Vector2(pe.pos.x, pe.pos.y - 1.8), 0.5, 0.5)
    projectile.physics_update = physics.projectile_physics
    projectile.vel = pe.view_direction*euclid.Vector2(10, 0)
  
  def can_jump(self):
    return self.entity.on_floor
  
  def jump(self, amount):
    pe = self.entity
    if pe.view_direction < 0:
      pe.state = 'jump_roll_right'
    else:
      pe.state = 'jump_roll_left'
    pe.jump_force.y = amount
    if amount != 0:
      pe.vel.y -= 16
    elif pe.vel.y < 0:
      pe.vel.y = 0


projectile_id = 0
def next_projectile_name():
  global projectile_id
  projectile_id += 1
  return "projectile "+str(projectile_id)
