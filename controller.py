#!/usr/bin/env python
# encoding: utf-8
"""
controller.py

Created by Joachim Bengtsson on 2009-03-28.
Copyright (c) 2009 Third Cog Software. All rights reserved.
"""

import sys
import os
import model

class GameController(object):
  """hej"""
  def __init__(self):
    super(Controller, self).__init__()
    
    self.game = model.Game()
    self.view = None
    


"""
class Jocke:
  def __init__(self):
    self.hair_length = 5
    self.procrastination_level = levels.MAX
    
  def frame(self):
    
    self.toilet_need = self.toilet_need + 1
    
    if random.randInt(0, 50) == 3:
      print "Auuurghh"
    else if self.boredom > 10:
      self.fiddle_with_iphone(5)
    
    def fiddle_with_iphone(self, duration):
      self.equip(self.items[IPHONE])
      



jocke = Jocke()

jocke.run()"""