# encoding: utf-8

from pyglet.gl import *

import euclid


tiles_drawn = 0


class View(object):
  """docstring for View"""
  def __init__(self, game):
    super(View, self).__init__()
    
    self.game = game
    self.level_view = LevelView(game)
    
    self.follow = None
    
  def draw(self):
    
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    
    # Move camera to correct position
    if self.follow is not None:
      
      self.cam = euclid.Vector2(self.follow.pos.x, self.follow.pos.y);
      self.cam.x -= 10.0
      self.cam.y -= 10.0
      
      if self.cam.x < 0.0: self.cam.x = 0.0
      elif self.cam.x > self.game.level.main_layer.tilemap.width - 20: self.cam.x = self.game.level.main_layer.tilemap.width - 20
      if self.cam.y < 0.0: self.cam.y = 0.0
      elif self.cam.y > self.game.level.main_layer.tilemap.height - 15: self.cam.y = self.game.level.main_layer.tilemap.height - 15

      #glTranslatef(-self.cam.x, -self.cam.y, 0)
      
      self.level_view.draw(self.cam)
        
  def update(self, dt):
    self.level_view.update(dt)
    
    
    

class LevelView(object):
  """docstring for LevelView"""
  def __init__(self, game):
    super(LevelView, self).__init__()
    
    self.game = game
    
    self.entity_views = []
    self.background_views = []
    self.main_view = None
    self.foreground_views = []
    
    for l in self.game.level.backgrounds:
      self.background_views.append( LayerView(self.game, l) )
      
    for l in self.game.level.foregrounds:
      self.foreground_views.append( LayerView(self.game, l) )
      
    self.main_view = LayerView(self.game, self.game.level.main_layer)
    
  def draw(self, cam):
    global tiles_drawn
      
    tiles_drawn = 0
    
    for bg in self.background_views:
      bg.draw(cam)
      
    for e in self.entity_views:
      e.draw(cam)
      
    self.main_view.draw(cam)
    
    for fg in self.foreground_views:
      fg.draw(cam)
      
    #print "Tiles drawn:", tiles_drawn
      
  def update(self, dt):
    for e in self.entity_views:
      e.update(dt)
      
  def view_for_entity(self, entity):
    for e in self.entity_views:
      if e.entity is entity: return e
    return None
      
  def entity_state_updated_for(self, entity):
    view = self.view_for_entity(entity)
    view.entity_state_updated()
  
  def entity_removed(self, entity):
    entView = self.view_for_entity(entity)
    self.entity_views.remove(entView)

class LayerView(object):
  """docstring for LayerView"""
  def __init__(self, game, layer):
    super(LayerView, self).__init__()
    
    self.game = game
    self.layer = layer

  def draw(self, cam):    
    global tiles_drawn
    ts = self.game.level.tilesets[0]
    
    position = euclid.Vector2(-cam.x * self.layer.scroll.x, -cam.y * self.layer.scroll.y)
    
    glPushMatrix()
    glTranslatef(position.x, position.y, 0)
  
    glBindTexture(GL_TEXTURE_2D, ts.texture().data.id)
    
    tm = self.layer.tilemap.map
                            
    glColor3f(self.layer.color.r, self.layer.color.g, self.layer.color.b)
    
    # Cull everything outside viewport
    r = int(-position.y)
    c = int(-position.x)
    
    re = r + 16
    ce = c + 21
    if re > len(tm): re = len(tm)
    if ce > len(tm[0]): ce = len(tm[0])
        
    glBegin(GL_QUADS)
    for y in range(r, re):
      for x in range(c, ce):
      
        tile = tm[y][x]
        
        if tile == 0:
          continue
          
        texcoords = ts.coords_for_tile(tile - 1)
        
        glTexCoord2f(texcoords.b().x, texcoords.b().y)
        glVertex2f(x,y)
        glTexCoord2f(texcoords.a().x, texcoords.a().y)
        glVertex2f(x,y+1)
        glTexCoord2f(texcoords.d().x, texcoords.d().y)
        glVertex2f(x+1,y+1)
        glTexCoord2f(texcoords.c().x, texcoords.c().y)
        glVertex2f(x+1,y)
        
        tiles_drawn += 1
        
    glEnd()
    
    glPopMatrix()
    
         
class SpriteView(object):
  """docstring for SpriteView"""
  def __init__(self, entity, sprite):
    super(SpriteView, self).__init__()

    # Härifrån kommer positioner och sånt skit
    self.entity = entity
    
    # Här kommer den grafiska datan
    self.sprite = sprite
    
    # Vilket håll spriten tittar. Detta har inget att göra med
    # vilket håll entityn är på väg. Det är dessutom inte nån
    # vektor-riktning utan mer "höger" och "vänster" och kanske "uppåt"
    self.dir = 0
    
    self.current_animation = None
    self.current_frame = 0
    
  def set_animation(self, anim_name):
    self.current_animation = self.sprite.animations[anim_name]
    self.current_frame = 0
    
  def draw(self, cam):
    if self.current_animation is None: return
    
    pos = self.entity.pos - self.current_animation.center
    texcoords = self.current_animation.coords_for_frame(self.current_frame)
    w = self.current_animation.size.x
    h = self.current_animation.size.y
    
    a = texcoords.a()
    b = texcoords.b()
    c = texcoords.c()
    d = texcoords.d()
  
    glPushMatrix()
    if self.current_animation.flipx:
      a, d = d, a
      b, c = c, b
    
    if self.current_animation.flipy: 
      a, b = b, a
      d, c = c, d
      
      
      #fx = 1.0
      #fy = 1.0
      #if self.current_animation.flipx: fx = -1.0
      #if self.current_animation.flipy: fy = -1.0
    glTranslatef(-cam.x + pos.x, -cam.y + pos.y, 0)
    
        
    glBindTexture(GL_TEXTURE_2D, self.current_animation.texture().data.id)
    
    glBegin(GL_QUADS)
    
    glTexCoord2f(b.x, b.y)
    glVertex2f(0,0)
    glTexCoord2f(a.x, a.y)
    glVertex2f(0,h)
    glTexCoord2f(d.x, d.y)
    glVertex2f(w,h)
    glTexCoord2f(c.x, c.y)
    glVertex2f(w,0)
    
    glEnd()
    
    glPopMatrix()    
    
    glPushAttrib(GL_ENABLE_BIT)
    glDisable(GL_TEXTURE_2D)
    
    bb = self.entity.boundingbox.translate(self.entity.pos - cam)
    
    glColor3f(1,0,1)
    
    glBegin(GL_LINE_LOOP)
    glVertex2f(bb.a().x, bb.a().y)
    glVertex2f(bb.b().x, bb.b().y)
    glVertex2f(bb.c().x, bb.c().y)
    glVertex2f(bb.d().x, bb.d().y)
    glEnd()
    
    glPopAttrib()
    
    

  def update(self, dt):
    
    #print "Uppdaterar SPRITE"
    
    self.current_frame = self.current_frame + 1
    if self.current_frame >= self.current_animation.num_frames:
      self.current_frame = self.current_animation.loopstart
            
      
  def entity_state_updated(self):
    if self.entity.state == "running_left":
      self.set_animation("run_left")
    elif self.entity.state == "running_right":
      self.set_animation("run_right")
    elif self.entity.state == "jump_roll_left":
      self.set_animation("jump_roll_left")
    elif self.entity.state == "jump_roll_right":
      self.set_animation("jump_roll_right")