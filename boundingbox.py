# encoding: utf-8

import euclid

class BoundingBox (object):
  min = None
  max = None
  def __init__(self, min, max):
    super(BoundingBox, self).__init__()
    self.min = min
    self.max = max
  
  def translate(self, point):
    return BoundingBox(self.min + point, self.max + point)

  def a(self):
    return self.min
  
  def b(self):
    return euclid.Vector2(self.min.x, self.max.y)
  
  def c(self):
    return self.max

  def d(self):
    return euclid.Vector2(self.max.x, self.min.y)
  
