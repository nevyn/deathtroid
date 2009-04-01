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


class Deathtroid(window.Window):
  """docstring for Deathtroid"""
  def __init__(self, argv):
    super(Deathtroid, self).__init__(640, 480, "DEATHTROID")
    glPointSize(5)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_FASTEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);

    glEnable(GL_TEXTURE_2D)

    self.server = self.client = self.menu = None

    self.current_tile = 0
    self.num_tiles = 14
    
    self.editor_open = False

    if (len(argv) == 3 or len(argv) == 4):

      roles = argv[2]
      name = argv[1]
      if(roles == "client"): 
        host = argv[3]
        self.start_game(roles, name, host)
      else:
        self.start_game(roles, name)


      #if(roles == "server" or roles == "both"):
      #  server = server_controller.ServerController()
      #  clock.schedule_interval(server.update, 1./30.)

      #if(roles == "client" or roles == "both"):
      #  host = "localhost"
      #  if(roles == "client"): host = sys.argv[3]
      #  client = client_controller.ClientController(name, host)
      #  clock.schedule(client.update)

    else:
      print "Usage: python main.py {playerName} [server|client {host}|both]"
      self.start_menu()

  def start_game(self, controller, player_name = "Samus", host="localhost", game_name = "Deathroid"):
    self.menu = None
    
    if controller == "server" or controller == "both":
      if self.server == None:
        self.server = server_controller.ServerController(game_name)
      clock.schedule_interval(self.server.update, 1./30.)
    
    if controller == "client" or controller == "both":
      if self.client == None:
        self.client = client_controller.ClientController(player_name, host)
      clock.schedule(self.client.update)
    

  def start_menu(self):
  
    self.server = None
    self.client = None
    if self.menu == None:
      self.menu = menu_controller.MenuController(self)
    clock.schedule(self.menu.update)
    
    

  def on_resize(self, width, height):
    if self.client:
      glViewport(0, 0, width, height)
      glMatrixMode(gl.GL_PROJECTION)
      glLoadIdentity()
      glOrtho(0, 20, 15, 0, -1, 1)
      glMatrixMode(gl.GL_MODELVIEW)
    
    elif self.menu:
      self.menu.resize(width, height)
  
    return pyglet.event.EVENT_HANDLED

  def on_draw(self):
    if self.client:
      self.client.draw()
      self.editor_draw()
    elif self.menu:
      self.clear()
      self.menu.draw()

  def on_key_press(self, symbol, modifiers):
    if self.client:
      self.event = None
    
      if symbol == key.LEFT:
        self.client.action("move_left")
      elif symbol == key.RIGHT:
        self.client.action("move_right")
      
      elif symbol == key.Z:
        self.client.action("jump")
      
      elif symbol == key.X:
        self.client.action("fire")
      
    elif self.menu:
      if symbol == key.ENTER:
        self.menu.keyboard_event("pressed_enter")

  def on_key_release(self, symbol, modifiers):
    if self.client:
      if symbol == key.LEFT:
        self.client.action("stop_moving_left")
      elif symbol == key.RIGHT:
        self.client.action("stop_moving_right")
      
      elif symbol == key.Z:
        self.client.action("stop_jump")
      
      elif symbol == key.X:
        self.client.action("stop_fire")
      
      
      elif symbol == key.F:
        self.set_fullscreen(fullscreen)
      
      elif symbol == key.S:
        layerfile = open('data/levels/foolevel/main.layer', 'r')
        old = demjson.decode(layerfile.read())
        layerfile.close()
      
        old["map"] = self.server.game.level.main_layer.tilemap.map
      
        new = demjson.encode(old)
      
      
        layerfile = open('data/levels/foolevel/main.layer', 'w')
        layerfile.write(new)
        layerfile.close()
        print "sparade!"

  def on_close(self):
      #reactor.stop()

      # Return true to ensure that no other handlers
      # on the stack receive the on_close event
      return True



  def tile_under_cursor(self, x, y):
    y = 480 - y

    vp = euclid.Vector2(self.client.view.cam.x*32, self.client.view.cam.y*32)

    x += vp.x
    y += vp.y

    x = int(x)
    y = int(y)

    x /= 32
    y /= 32
    return (x, y)

  def editor_draw(self):
    if not self.editor_open:
      return
  
    ts = self.client.view.level_view.main_view.layer.tileset
    ts.texture().bind()
    w = len(ts.tiles)+3
    glTranslatef(1,0,0)
    glScalef(w, 1, 1)
  
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 1.0)
    glVertex2f(0,     0)
  
    glTexCoord2f(0.0, 0.0)
    glVertex2f(0,     1)
  
    glTexCoord2f(1.0, 0.0)
    glVertex2f(1, 1)
  
    glTexCoord2f(1.0, 1.0)
    glVertex2f(1, 0)
    glEnd()
  
  
  def on_mouse_press(self, x, y, button, modifiers):
    server = self.server
    client = self.client
    if self.menu:
      if button == pyglet.window.mouse.LEFT:
        self.menu.mouse_pressed(x, y)
    elif client and server:
      if button == window.mouse.RIGHT:
        self.editor_open = True

  def on_mouse_release(self, x, y, button, modifiers):
  
    if button == window.mouse.LEFT:
      (x, y) = self.tile_under_cursor(x, y)
      self.server.game.level.main_layer.tilemap.map[y][x] = self.current_tile
      self.client.game.level.main_layer.tilemap.map[y][x] = self.current_tile
  
    if button == window.mouse.RIGHT:
      tx = x/32
      ty = (480-y)/32
  
      if ty > 0 or tx > len(self.client.view.level_view.main_view.layer.tileset.tiles):
        (x, y) = self.tile_under_cursor(x, y)
        self.current_tile = self.server.game.level.main_layer.tilemap.map[y][x]
        print "chose ", self.current_tile
      else:
        self.current_tile = tx
        print "chose from palette ", self.current_tile
  
    self.editor_open = False

  def on_mouse_motion(self, x, y, dx, dy):
    if self.menu:
      self.menu.mouse_moved(x, y)



#reactor.run()
game = Deathtroid(sys.argv)
pyglet.app.EventLoop().run()