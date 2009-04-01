# encoding: utf-8

import euclid
import math
import logics

def calc_velocity(vel, acc, max_vel, dt):
  vel += acc * dt

  if vel.x < -max_vel.x:
    vel.x = -max_vel.x
  elif vel.x > max_vel.x:
    vel.x = max_vel.x
  
  return vel

def calc_acceleration(forces, mass):
  inv_mass = 1.0 / mass
  return reduce(lambda acc, f: acc + f * inv_mass, forces)

def is_colliding(a, b):
  bba = a.boundingbox.translate(a.pos)
  bbb = b.boundingbox.translate(b.pos)
  return bba.is_overlapping(bbb)

def collision(tilemap, bb):
  return tilemap.intersection(bb.a(), bb.b()) or tilemap.intersection(bb.b(), bb.c()) or tilemap.intersection(bb.c(), bb.d()) or tilemap.intersection(bb.d(), bb.a()) or None

class Physics(object):
  def __init__(self, game):
    super(Physics, self).__init__()
    self.game = game
  
  def initializeEntity(self, entity, **args):
    classes = {
      "force": ForcebasedPhysics,
      "static" : StaticPhysics,
      "projectile": ProjectilePhysics
    }
    entity.physics = None
    if entity.physicsName in classes:
      print 'creating physics class', entity.physicsName, 'with args', args
      entity.physics = classes[entity.physicsName](entity, **args)

class PhysicsModel(object):
  def __init__(self, entity):
    super(PhysicsModel, self).__init__()
    self.entity = entity
  
  def update(self, tilemap, dt):
    pass

class ForcebasedPhysics(PhysicsModel):
  def __init__(self, entity, mass = None):
    super(ForcebasedPhysics, self).__init__(entity)
    self.mass = mass
  
  def update(self, tilemap, dt):
    ent = self.entity
    
    gravity = ent.level.gravity() * self.mass
    forces = [ent.move_force, ent.jump_force, gravity]
    
    ent.acc = calc_acceleration(forces, self.mass)
    ent.vel = calc_velocity(ent.vel, ent.acc, ent.max_vel, dt)
    if ent.jump_force.y < 0:
      ent.jump_force.y -= ent.vel.y

    new_pos = ent.pos + ent.vel * dt
    
    bb = ent.boundingbox
    
    vertical_collision = collision(tilemap, bb.translate(euclid.Vector2(ent.pos.x, new_pos.y)))
    horizontal_collision = collision(tilemap, bb.translate(euclid.Vector2(new_pos.x, ent.pos.y)))
    
    ent.on_floor = ent.vel.y > 0 and vertical_collision != None
    ent.on_wall = ent.vel.x != 0 and horizontal_collision != None
    
    if vertical_collision != None:
      ent.vel.y = 0
        
      # On the way down we want to land exactly on the ground. Usually this
      # isn't the case since the velocity is too great and would cause it to
      # "jump" down a bit the next frame. By setting the position to the ceil
      # value we assure that we are always on the ground. However, we don't want
      # to be IN the ground but right above it we subtract with a very small
      # value.
      if ent.on_floor:
        (x,y) = vertical_collision
        while tilemap.tile_at_point(euclid.Vector2(x,y)) != 0:
          y -= 1
        ent.pos.y = y+1-0.0000000001
    else:
      ent.pos.y = new_pos.y
    
    if horizontal_collision != None:
      pass
    else:
       ent.pos.x = new_pos.x

class StaticPhysics(PhysicsModel):
  def __init__(self, entity):
    super(StaticPhysics, self).__init__(entity)
  
class ProjectilePhysics(PhysicsModel):
  def __init__(self, entity):
    super(ProjectilePhysics, self).__init__(entity)
  
  def update(self, tilemap, dt):
    ent = self.entity
    
    ent.pos += ent.vel*dt

    col = collision(tilemap, ent.boundingbox.translate(euclid.Vector2(ent.pos.x, ent.pos.y)))
    if col != None:
      (x,y) = col
      ent.level.game.delegate.entitiesCollidedAt(ent, None, col)
