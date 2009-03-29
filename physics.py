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
  return tilemap.intersection(bb.a(), bb.b()) or tilemap.intersection(bb.b(), bb.c()) or tilemap.intersection(bb.c(), bb.d()) or tilemap.intersection(bb.d(), bb.a()) or None

def forcebased_physics(ent, tilemap, dt):
    gravity = ent.level.gravity() * ent.mass
    forces = [ent.move_force, ent.jump_force, gravity]
    
    ent.acc = calc_acceleration(forces, ent.mass)
    ent.vel = calc_velocity(ent.vel, ent.acc, ent.max_vel, dt)
    if ent.jump_force.y < 0:
      ent.jump_force.y -= ent.vel.y

    new_pos = ent.pos + ent.vel * dt
    
    bb = ent.boundingbox()
    
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
        ent.pos.y = y-0.0000000001
    else:
      ent.pos.y = new_pos.y
    
    if horizontal_collision != None:
      pass
    else:
       ent.pos.x = new_pos.x
    
def static_physics(ent, tilemap, dt):
  pass

def fulfysik(ent, tilemap, dt):
  ent.pos.x += 1.3 * dt
