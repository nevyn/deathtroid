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
  if game_controller:
    glViewport(0, 0, width, height)
    glMatrixMode(gl.GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, 20, 15, 0, -1, 1)
    glMatrixMode(gl.GL_MODELVIEW)
    return pyglet.event.EVENT_HANDLED

@win.event
def on_draw():
  if game_controller:
    #win.clear()
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    
    game_controller.draw()

@win.event
def on_key_press(symbol, modifiers):
  if game_controller:
    event = None
    
    if symbol == key.LEFT:
      game_controller.action("move_left")
    elif symbol == key.RIGHT:
      game_controller.action("move_right")
    elif symbol == key.UP:
      game_controller.action("jump")

@win.event
def on_key_release(symbol, modifiers):
  if game_controller:
    if symbol == key.LEFT:
      game_controller.action("stop_moving_left")
    elif symbol == key.RIGHT:
      game_controller.action("stop_moving_right")



glPointSize(5)
glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_FASTEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);

if(len(sys.argv) < 3):
  print "Usage: python main.py {playerName} [server|client|both]"

roles = sys.argv[2]
name = sys.argv[1]

server_controller = game_controller = None

if(roles == "server" or roles == "both"):
  server_controller = controller.ServerController()
  clock.schedule(server_controller.update)

if(roles == "client" or roles == "both"):
  game_controller = controller.GameController(name)
  clock.schedule(game_controller.update)


app.run()