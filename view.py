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
    
    glColor3f(1., 1., 1.)
    
    for y, row in enumerate(tm):
      for x, tile in enumerate(row):
        
        if tile == 0:
          continue
        
        glBegin(GL_QUADS)
        
        glColor3f(0.5, 0.5, 0.5)
        glVertex2i(x, y)
        glColor3f(0.2,0.2,0.2)
        glVertex2i(x, y + 1)
        glColor3f(1.0,1.0,1.0)
        glVertex2i(x + 1, y + 1)
        glVertex2i(x + 1, y)
        
        glEnd()
        
    entities = self.game.level.entities
    
    for e in entities:
      glBegin(GL_POINTS)
      
      glVertex2f(e.pos.x, e.pos.y)
      
      glEnd()