#!/usr/bin/env python
# encoding: utf-8

from pyglet.gl import *

import euclid

class View(object):
  """docstring for View"""
  def __init__(self, game):
    super(View, self).__init__()
    
    self.game = game
    self.level_view = LevelView(game)
    
    self.entity_views = []
    
    self.follow = None
    
  def draw(self):
    
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    
    # Move
    if self.follow is not None:
      
      cam = euclid.Vector2(self.follow.pos.x, self.follow.pos.y);
      cam.x -= 10.0
      cam.y -= 10.0
      
      if cam.x < 0.0: cam.x = 0.0
      elif cam.x > self.game.level.tilemap.width - 20: cam.x = self.game.level.tilemap.width - 20
      if cam.y < 0.0: cam.y = 0.0
      elif cam.y > self.game.level.tilemap.height - 15: cam.y = self.game.level.tilemap.height - 15

      
      glTranslatef(-cam.x, -cam.y, 0)
    
        
    
    # Draw background layers
    
    # Draw collision layer
    self.level_view.draw()
    
    # Draw entities
    for e in self.entity_views:
      e.draw()
    
    # Draw foreground layers
    
    
  def update(self, dt):
    for e in self.entity_views:
      e.update(dt)    
    
    
    

class LevelView(object):
  """docstring for LevelView"""
  def __init__(self, game):
    super(LevelView, self).__init__()
    
    self.game = game
    
  
  def draw(self):
    
    tm = self.game.level.tilemap.map
    ts = self.game.level.tilesets[0]
    
    glColor3f(1., 1., 1.)
    
    for y, row in enumerate(tm):
      for x, tile in enumerate(row):
        
        if tile == 0:
          continue
        
        ts.tiles[tile - 1].anchor_y = 16
        tl = ts.tiles[tile - 1].get_transform(flip_y=True)
        
        tl.blit(x,y, width=1, height=1)
        
    entities = self.game.level.entities
    
        
         
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
    print "set animation to ", anim_name , " : ", self.current_animation
    
  def draw(self):
    pos = self.entity.pos - self.sprite.center
    texcoords = self.current_animation.coords[self.current_frame]
    w = self.sprite.width
    h = self.sprite.height
    

    
    glPushMatrix()
    glTranslatef(pos.x, pos.y, 0)
    
    #glColor3f(1.0, 0.0, 0.0)
    
    #glBegin(GL_QUADS)    

    #glVertex2f(0,0)
    #glVertex2f(0,h)
    #glVertex2f(w,h)
    #glVertex2f(w,0)
    
    #glEnd()
    glEnable(GL_TEXTURE_2D)
    
    glBindTexture(GL_TEXTURE_2D, self.current_animation.texture.data.id)
    
    
    glBegin(GL_QUADS)    


    #glTexCoord2f(0.0, 0.0)
    #glVertex2f(0,0)
    #glTexCoord2f(0.0, 1.0)
    #glVertex2f(0,h)
    #glTexCoord2f(1.0, 1.0)
    #glVertex2f(w,h)
    #glTexCoord2f(1.0, 0.0)
    #glVertex2f(w,0)

    
    glTexCoord2f(texcoords.b().x, texcoords.b().y)
    glVertex2f(0,0)
    glTexCoord2f(texcoords.a().x, texcoords.a().y)
    glVertex2f(0,h)
    glTexCoord2f(texcoords.d().x, texcoords.d().y)
    glVertex2f(w,h)
    glTexCoord2f(texcoords.c().x, texcoords.c().y)
    glVertex2f(w,0)
    
    glEnd()
    
    glPopMatrix()
    
    bb = self.entity.boundingbox().translate(self.entity.pos)
    
    glDisable(GL_TEXTURE_2D)
    
    glColor3f(1.0, 1.0, 0.0)
    
    glBegin(GL_LINE_LOOP)
    
    glVertex2f(bb.a().x, bb.a().y)
    glVertex2f(bb.b().x, bb.b().y)
    glVertex2f(bb.c().x, bb.c().y)
    glVertex2f(bb.d().x, bb.d().y)
    
    glEnd()           
    

  def update(self, dt):
    self.current_frame = self.current_frame + 1
    if self.current_frame >= self.current_animation.frames:
      self.current_frame = self.current_animation.loopstart
     