import logics
from boundingbox import *
from pyglet import clock
import model
import uuid


class ProjectileBehavior(logics.Behavior):
  """Behavior for anything fired from a gun."""
  def __init__(self, entity, logic, firingEntity, **args):
    super(ProjectileBehavior, self).__init__(entity, logic)
    entity.vel = firingEntity.view_direction*euclid.Vector2(20, 0)
    entity.name = next_anonymous_name(self)
    
    self.firingEntity = firingEntity
    
    self.play_sound("BaseShot")
    
    if firingEntity.view_direction == 1:
      entity.state = ["r"]
    else:
      entity.state = ["l"]
  
  def collided(self, other):
    if not other or (other != self.firingEntity and other.behaviorName != "projectile"):
      model.Entity(self.entity.level, "smallexplosion", None, self.entity.pos.copy())
      self.entity.remove()
      

class ExplosionBehavior(logics.Behavior):
  def __init__(self, entity, logic, **args):
    super(ExplosionBehavior, self).__init__(entity, logic)
    
    entity.name = next_anonymous_name(self)
    entity.state = ["explode"]
    
    self.play_sound("Burst")
    
    clock.schedule_once(self.remove, .24)
    
  def remove(self, *asdf):
    self.entity.remove()
    

anonymous_id = 0
def next_anonymous_name(beha):
  global anonymous_id
  anonymous_id += 1
  return "temporary "+beha.entity.type+" entity #"+str(anonymous_id)
