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
import controller

win = window.Window(640, 480, "DEATHTROID")

@win.event
def on_draw():
    win.clear()
    


game_controller = controller.GameController()



clock.schedule(game_controller.update)


app.run()