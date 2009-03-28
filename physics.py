# encoding: utf-8

import euclid

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

def entity_update(ent, tilemap, dt):
    new_pos = ent.pos + ent.vel * dt
      
    ent.on_floor = tilemap.tile_at_point(euclid.Vector2(ent.pos.x, new_pos.y)) != 0
    
    if ent.on_floor:
      ent.vel.y = 0
      
      # On floor with no walls
      if tilemap.tile_at_point(euclid.Vector2(new_pos.x, ent.pos.y)) == 0:
        ent.pos.x = new_pos.x
    else:
      # Falling
      if tilemap.tile_at_point(new_pos) == 0:
        ent.pos = new_pos
      
      # Falling but pushing against wall
      else:
        ent.pos.y = new_pos.y
    
    gravity = ent.level.game.gravity() * ent.mass
    
    ent.acc = calc_acceleration([ent.move_force, gravity], ent.mass)
    ent.vel = calc_velocity(ent.vel, ent.acc, ent.max_vel, dt)
    
    print ent.pos, ent.vel, ent.on_floor
