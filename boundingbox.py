# encoding: utf-8

import euclid

class BoundingBox (object):
  min = None
  max = None
  def __init__(self, _min, _max):
    super(BoundingBox, self).__init__()
    self.min = _min
    self.max = _max
    
    self.pa = self.min
    self.pb = euclid.Vector2(self.min.x, self.max.y)
    self.pc = self.max
    self.pd = euclid.Vector2(self.max.x, self.min.y)
  
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
  
  def __repr__(self):
    return 'BoundingBox: (%f, %f) - (%f, %f)' % (self.min.x, self.min.y, self.max.x, self.max.y)
  
