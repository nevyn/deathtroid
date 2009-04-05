import logics
from boundingbox import *
from pyglet import clock
import model
import uuid

def volumeIncreaseCallback(voice):
  if voice.volume < 0.6:
    voice.volume += 0.05


class AvatarBehavior(logics.Behavior):
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
    
    self.healthDangerSoundID = None
    
    self.health = 100
    
  def fire(self):
    pe = self.entity
    projectile = model.Entity(pe.level, "bullet1", None, euclid.Vector2(pe.pos.x, pe.pos.y - 1.8), behavior={'firingEntity': pe})
  
  def can_jump(self):
    return self.entity.on_floor
  
  def jump(self, amount):
    pe = self.entity
    pe.jump_force.y = amount
    if amount != 0:
      self.entity.boundingbox = self.jump_bb
      pe.add_state("jump")
      
      self.spinSoundID = uuid.uuid4().hex
      self.logic.play_sound("Spin", {"follow": pe.name, "id":  self.spinSoundID, "loop": True, "callback": volumeIncreaseCallback, "volume": 0.1})
      
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
    self.play_sound("Land")
  
  def collided(self, other):
    if other and other.behaviorName == "projectile" and other.behavior.firingEntity != self.entity:
      self.damage(10)
  
  def damage(self, amount):
    self.health -= 10
    self.play_sound("Injured")
    
    print "Health", self.health
    
    if self.health <= 30 and not self.healthDangerSoundID:
      self.healthDangerSoundID = uuid.uuid4().hex
      #self.logic.play_sound("HealthWarning", {"follow": self.entity.name, "id":  self.healthDangerSoundID, "loop": True, "volume": 0.05, "private_for_player", self.entity.player.name})
      
    
    if self.health <= 0:
      other.behavior.firingEntity.player.score += 1
      self.die()
    
  
  def die(self):
    self.entity.player.set_entity(None)
    self.entity.remove()
  
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
    
    clock.schedule_once(self.remove, .5)
    
  def remove(self, *asdf):
    self.entity.remove()
    

anonymous_id = 0
def next_anonymous_name(beha):
  global anonymous_id
  anonymous_id += 1
  return "temporary "+beha.entity.type+" entity #"+str(anonymous_id)
