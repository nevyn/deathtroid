# encoding: utf-8

class Logic(object):
  """Logic handler; what to do with player input, collisions, etc"""
  def __init__(self):
    super(Logic, self).__init__()
    
  def collision(self, a, b, point):
    (x,y) = point
    print 'collition between %s and %s at tile %dx%d' % (a,b,x,y)
    a.vel.x = 0
    a.vel.y = 0
    a.remove()
