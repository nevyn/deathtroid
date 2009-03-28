# encoding: utf-8

import euclid
import math

def calc_velocity(vel, acc, max_vel, dt):
  vel += acc * dt
    
  if vel.x < -max_vel.x:
    vel.x = -max_vel.x
  elif vel.x > max_vel.x:
    vel.x = max_vel.x
    
  if vel.y < -max_vel.y:
    vel.y = -max_vel.y
  elif vel.y > max_vel.y:
    vel.y = max_vel.y
  
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

def entity_update(ent, tilemap, dt):
    new_pos = ent.pos + ent.vel * dt
    
    bb = ent.boundingbox()
    ent.on_floor = collision(tilemap, bb.translate(euclid.Vector2(ent.pos.x, new_pos.y)))
    
    if ent.on_floor:
      ent.vel.y = 0
      
      # On floor with no wall s
      if collision(tilemap, bb.translate(euclid.Vector2(new_pos.x, ent.pos.y))) == 0:
        ent.pos.x = new_pos.x
    else:
      # Falling
      if collision(tilemap, bb.translate(new_pos)) == 0:
        ent.pos = new_pos
      
      # Falling but pushing against wall
      else:
        ent.pos.y = new_pos.y
    
    gravity = ent.level.game.gravity() * ent.mass
    
    ent.acc = calc_acceleration([ent.move_force, gravity], ent.mass)
    ent.vel = calc_velocity(ent.vel, ent.acc, ent.max_vel, dt)
    
    #print ent.pos, ent.vel, ent.on_floor
