#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Joachim Bengtsson on 2009-03-28.
Copyright (c) 2009 Third Cog Software. All rights reserved.
"""

import sys
import os
from pyglet import window
from pyglet import app
from pyglet import clock
from pyglet.gl import *
from pyglet.window import key
import controller
import logging

logging.basicConfig(level=logging.WARNING)

win = window.Window(640, 480, "DEATHTROID")

@win.event
def on_resize(width, height):
  glViewport(0, 0, width, height)
  glMatrixMode(gl.GL_PROJECTION)
  glLoadIdentity()
  glOrtho(0, 20, 15, 0, -1, 1)
  glMatrixMode(gl.GL_MODELVIEW)
  return pyglet.event.EVENT_HANDLED

@win.event
def on_draw():
    #win.clear()
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    
    game_controller.draw()

@win.event
def on_key_press(symbol, modifiers):
  if symbol == key.LEFT:
    pe.entity.set_movement(-2,0)
  elif symbol == key.RIGHT:
    pe.entity.set_movement(2,0)
  elif symbol == key.UP:
    if pe.entity.can_jump():
      pe.entity.set_movement(0,-500)


@win.event
def on_key_release(symbol, modifiers):
  if symbol == key.LEFT:
    pe.entity.set_movement(2,0)
  if symbol == key.RIGHT:
    pe.entity.set_movement(-2,0)

glPointSize(5)
glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_FASTEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);

    

server_controller = controller.ServerController()

game_controller = controller.GameController()
pe = server_controller.ful_get_player(0)
print 'pe: ', pe

clock.schedule(server_controller.update)
clock.schedule(game_controller.update)


app.run()