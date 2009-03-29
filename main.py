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

#import pygletreactor
#pygletreactor.install()
#from twisted.internet import reactor

import client_controller
import server_controller
import logging
import euclid
import demjson


logging.basicConfig(level=logging.WARNING)

win = window.Window(640, 480, "DEATHTROID")

current_controller = None

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
    game_controller.draw()

@win.event
def on_key_press(symbol, modifiers):
  if game_controller:
    event = None
    
    if symbol == key.LEFT:
      game_controller.action("move_left")
    elif symbol == key.RIGHT:
      game_controller.action("move_right")
      
    elif symbol == key.Z:
      game_controller.action("jump")
      
    elif symbol == key.X:
      game_controller.action("fire")

@win.event
def on_key_release(symbol, modifiers):
  global fullscreen
  if game_controller:
    if symbol == key.LEFT:
      game_controller.action("stop_moving_left")
    elif symbol == key.RIGHT:
      game_controller.action("stop_moving_right")
      
    elif symbol == key.Z:
      game_controller.action("stop_jump")
      
      
    elif symbol == key.F:
      fullscreen = not fullscreen
      win.set_fullscreen(fullscreen)
      
    elif symbol == key.S:
      ubbe = demjson.encode(server.game.level.main_layer.tilemap.map)
      dfdfdf = open('data/levels/foolevel/main.layer', 'w')
      print dfdfdf
      dfdfdf.write(ubbe)
      print "sparade!"

@win.event
def on_close():
    #reactor.stop()

    # Return true to ensure that no other handlers
    # on the stack receive the on_close event
    return True


fullscreen = False

current_tile = 0
num_tiles = 14
  
@win.event
def on_mouse_press(x, y, button, modifiers):
  global current_tile
  y = 480 - y

  vp = euclid.Vector2(game_controller.view.cam.x*32, game_controller.view.cam.y*32)

  x += vp.x
  y += vp.y

  x = int(x)
  y = int(y)

  x /= 32
  y /= 32

  print "cam: ", game_controller.view.cam

  #x += game_controller.view.cam.x
  #y += int(game_controller.view.cam.y)


  print "sätt i ", x, y
  if button == window.mouse.LEFT:
    
    server.game.level.main_layer.tilemap.map[y][x] = (server.game.level.main_layer.tilemap.map[y][x] - 1) % num_tiles
    game_controller.game.level.main_layer.tilemap.map[y][x] = (game_controller.game.level.main_layer.tilemap.map[y][x] - 1) % num_tiles
    
  elif button == window.mouse.RIGHT:    
    server.game.level.main_layer.tilemap.map[y][x] = (server.game.level.main_layer.tilemap.map[y][x] + 1) % num_tiles
    game_controller.game.level.main_layer.tilemap.map[y][x] = (game_controller.game.level.main_layer.tilemap.map[y][x] + 1) % num_tiles    


glPointSize(5)
glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_FASTEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);

glEnable(GL_TEXTURE_2D)

if(len(sys.argv) < 3):
  print "Usage: python main.py {playerName} [server|client {host}|both]"

roles = sys.argv[2]
name = sys.argv[1]

server = game_controller = None

if(roles == "server" or roles == "both"):
  server = server_controller.ServerController()
  clock.schedule_interval(server.update, 1./30.)

if(roles == "client" or roles == "both"):
  host = "localhost"
  if(roles == "client"): host = sys.argv[3]
  game_controller = client_controller.ClientController(name, host)
  clock.schedule(game_controller.update)


#reactor.run()
pyglet.app.EventLoop().run()