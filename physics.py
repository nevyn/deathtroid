# encoding: utf-8

import euclid
import math

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

def collision(tilemap, bb):
  if tilemap.intersection(bb.a(), bb.b()): return True
  if tilemap.intersection(bb.b(), bb.c()): return True
  if tilemap.intersection(bb.c(), bb.d()): return True
  if tilemap.intersection(bb.d(), bb.a()): return True
  return False

def forcebased_physics(ent, tilemap, dt):
    new_pos = ent.pos + ent.vel * dt
    
    bb = ent.boundingbox()
    ent.on_floor = collision(tilemap, bb.translate(euclid.Vector2(ent.pos.x, new_pos.y)))
    
    if ent.on_floor:
      ent.vel.y = 0
      
      # On floor with no wall s
      if collision(tilemap, bb.translate(euclid.Vector2(new_pos.x, ent.pos.y))) == 0:
        ent.pos.x = new_pos.x
        
        # On the way down we want to land exactly on the ground. Usually this
        # isn't the case since the velocity is too great and would cause it to
        # "jump" down a bit the next frame. By setting the position to the ceil
        # value we assure that we are always on the ground. However, we don't want
        # to be IN the ground but right above it we subtract with a very small
        # value.
        if ent.vel.y < 0:
          ent.pos.y = math.ceil(ent.pos.y)-0.0000000001
    else:
      # Falling
      if collision(tilemap, bb.translate(new_pos)) == 0:
        ent.pos = new_pos
      
      # Falling but pushing against wall
      else:
        ent.pos.y = new_pos.y
    
    gravity = ent.level.game.gravity() * ent.mass
    
    ent.acc = calc_acceleration([ent.move_force, ent.jump_force, gravity], ent.mass)
    ent.vel = calc_velocity(ent.vel, ent.acc, ent.max_vel, dt)
    if ent.jump_force.y < 0:
      ent.jump_force.y -= ent.vel.y
    
def static_physics(ent, tilemap, dt):
  pass
