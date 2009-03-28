#!/usr/bin/env python
# encoding: utf-8

from pyglet.gl import *

class View(object):
  """docstring for View"""
  def __init__(self, game):
    super(View, self).__init__()
    
    self.game = game
    
  
  def draw(self):
    # kanske kan splöffa in detta i en egen view, typ LevelView, sen...
    
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
    
    for e in entities:
      glBegin(GL_POINTS)
      
      glVertex2f(e.pos.x, e.pos.y)
      
      glEnd()
      
      bb = e.boundingbox().translate(e.pos)
      
      glBegin(GL_QUADS)
      
      glVertex2f(bb.a().x, bb.a().y)
      glVertex2f(bb.b().x, bb.b().y)
      glVertex2f(bb.c().x, bb.c().y)
      glVertex2f(bb.d().x, bb.d().y)
      
      glEnd()
      
      #e.sprite.gfx.scale = 0.5 # float(0.03125)
      #e.sprite.gfx.x = e.pos.x
      #e.sprite.gfx.y = e.pos.y
      #e.sprite.gfx.draw()
         
         
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
    
  def draw(self):
    
    pos = self.entity.pos
    
    
     