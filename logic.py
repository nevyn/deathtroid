# encoding: utf-8

def collision(a, b, point):
  (x,y) = point
  print 'collition between %s and %s at tile %dx%d' % (a,b,x,y)
  a.vel.x = 0
  a.vel.y = 0
  a.remove()
