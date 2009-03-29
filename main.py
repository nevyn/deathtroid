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
import menu_controller
import logging
import euclid
import demjson


logging.basicConfig(level=logging.WARNING)

win = window.Window(640, 480, "DEATHTROID")


def start_game(controller, player_name = "Samus", host="localhost"):
  
  global menu, server, client
  menu = None
    
  if controller == "server" or controller == "both":
    if server == None:
      server = server_controller.ServerController()
    clock.schedule_interval(server.update, 1./30.)
    
  if controller == "client" or controller == "both":
    if client == None:
      client = client_controller.ClientController(player_name, host)
    clock.schedule(client.update)
    

def start_menu():
  
    global menu, server, client, win
    server = None
    client = None
    if menu == None:
      menu = menu_controller.MenuController(win)
    clock.schedule(menu.update)
    
    

@win.event
def on_resize(width, height):
  if client:
    glViewport(0, 0, width, height)
    glMatrixMode(gl.GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, 20, 15, 0, -1, 1)
    glMatrixMode(gl.GL_MODELVIEW)
    
  elif menu:
    menu.resize(width, height)
  
  return pyglet.event.EVENT_HANDLED

@win.event
def on_draw():
  if client:
    client.draw()
  elif menu:
    win.clear()
    menu.draw()

@win.event
def on_key_press(symbol, modifiers):
  if client:
    event = None
    
    if symbol == key.LEFT:
      client.action("move_left")
    elif symbol == key.RIGHT:
      client.action("move_right")
      
    elif symbol == key.Z:
      client.action("jump")
      
    elif symbol == key.X:
      client.action("fire")
      
  elif menu:
    if symbol == key.ENTER:
      menu.keyboard_event("pressed_enter")

@win.event
def on_key_release(symbol, modifiers):
  global fullscreen
  if client:
    if symbol == key.LEFT:
      client.action("stop_moving_left")
    elif symbol == key.RIGHT:
      client.action("stop_moving_right")
      
    elif symbol == key.Z:
      client.action("stop_jump")
      
    elif symbol == key.X:
      client.action("stop_fire")
      
      
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
  
  if menu:
    if button == pyglet.window.mouse.LEFT:
      menu.mouse_pressed(x, y)
  
  elif client and server:
    global current_tile
    y = 480 - y

    vp = euclid.Vector2(client.view.cam.x*32, client.view.cam.y*32)

    x += vp.x
    y += vp.y

    x = int(x)
    y = int(y)

    x /= 32
    y /= 32

    print "cam: ", client.view.cam

    #x += client.view.cam.x
    #y += int(client.view.cam.y)


    print "sätt i ", x, y
    if button == window.mouse.LEFT:
    
      server.game.level.main_layer.tilemap.map[y][x] = (server.game.level.main_layer.tilemap.map[y][x] - 1) % num_tiles
      client.game.level.main_layer.tilemap.map[y][x] = (client.game.level.main_layer.tilemap.map[y][x] - 1) % num_tiles
    
    elif button == window.mouse.RIGHT:    
      server.game.level.main_layer.tilemap.map[y][x] = (server.game.level.main_layer.tilemap.map[y][x] + 1) % num_tiles
      client.game.level.main_layer.tilemap.map[y][x] = (client.game.level.main_layer.tilemap.map[y][x] + 1) % num_tiles    


@win.event
def on_mouse_motion(x, y, dx, dy):
  if menu:
    menu.mouse_moved(x, y)


glPointSize(5)
glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_FASTEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);

glEnable(GL_TEXTURE_2D)

server = client = menu = None

if(len(sys.argv) < 3 and len(sys.argv) != 1):
  print "Usage: python main.py {playerName} [server|client {host}|both]"
  
elif (len(sys.argv) == 3):

  roles = sys.argv[2]
  name = sys.argv[1]
  if(roles == "client"): 
    host = sys.argv[3]
    start_game(roles, name, host)
  else:
    start_game(roles, name)
  

  #if(roles == "server" or roles == "both"):
  #  server = server_controller.ServerController()
  #  clock.schedule_interval(server.update, 1./30.)

  #if(roles == "client" or roles == "both"):
  #  host = "localhost"
  #  if(roles == "client"): host = sys.argv[3]
  #  client = client_controller.ClientController(name, host)
  #  clock.schedule(client.update)
    
else:
  start_menu()


#reactor.run()
pyglet.app.EventLoop().run()