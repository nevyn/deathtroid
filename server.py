#!/usr/bin/env python
# encoding: utf-8
"""
server.py

Created by Joachim Bengtsson on 2009-03-28.
Copyright (c) 2009 Third Cog Software. All rights reserved.
"""

import sys
import os
import controller
import time
import logging

logging.basicConfig(level=logging.WARNING)
game_controller = controller.ServerController()

while 1:
  game_controller.update(0.01)
  time.sleep(0.01)
