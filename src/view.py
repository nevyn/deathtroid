# encoding: utf-8

#from pyglet.gl import *

# Den här är fan så mycket snabbare än pyglet.gl. Ta reda på varför.
from OpenGL.GL import *

import euclid
import math


tiles_drawn = 0


class View(object):
  """docstring for View"""
  def __init__(self, game):
    super(View, self).__init__()
    
    self.game = game
    self.level_view = LevelView(game)
    
    self.cam_dest = euclid.Vector3(0.,0.,0.)
    self.cam = euclid.Vector2(0., 0.)
    
    self.follow = None
    
  def draw(self):
    
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
                
    # Move camera to correct position
    if self.follow is not None:
      
      self.cam_dest = euclid.Vector3(self.follow.pos.x + (4*self.follow.view_direction), self.follow.pos.y, 0.0)
      self.cam_dest.x -= 10.0
      self.cam_dest.y -= 7.5
      
      if self.cam_dest.x < 0.0: self.cam_dest.x = 0.0
      elif self.cam_dest.x > self.game.level.main_layer.tilemap.width - 20: self.cam_dest.x = self.game.level.main_layer.tilemap.width - 20
      if self.cam_dest.y < 0.0: self.cam_dest.y = 0.0
      elif self.cam_dest.y > self.game.level.main_layer.tilemap.height - 15: self.cam_dest.y = self.game.level.main_layer.tilemap.height - 15
      
      # move cam a little closer to cam_dest
      dist = euclid.Vector2(self.cam_dest.x - self.cam.x, self.cam_dest.y - self.cam.y)
      self.cam = self.cam + dist.normalized()
      
      #glTranslatef(-self.cam.x, -self.cam.y, 0)
      
      glTranslatef(-10,7.5, -18.0)
      glScalef(1,-1,1)
      
      self.level_view.draw(self.cam)
    
    glDisable(GL_TEXTURE_2D)
    glBegin(GL_LINES)
    glColor3f(1.0, 1.0, 1.0)
    glVertex2f(0,0)
    glVertex2f(0,2)
    glVertex2f(0,0)
    glVertex2f(2,0)
    glEnd()
    glEnable(GL_TEXTURE_2D)
  
        
  def update(self, dt):
    self.level_view.update(dt)
    
    
    

class LevelView(object):
  """docstring for LevelView"""
  def __init__(self, game):
    super(LevelView, self).__init__()
    
    self.game = game
    
    self.entity_views = []
    self.background_views = []
    self.main_view = None
    self.foreground_views = []
    
    for l in self.game.level.backgrounds:
      self.background_views.append( LayerView(self.game, l) )
      
    for l in self.game.level.foregrounds:
      self.foreground_views.append( LayerView(self.game, l) )
      
    self.main_view = LayerView(self.game, self.game.level.main_layer)
    
  def draw(self, cam):
    global tiles_drawn
      
    tiles_drawn = 0
        
    for bg in self.background_views:
      bg.draw(cam)
      
    for e in self.entity_views:
      e.draw(cam)
    
    self.main_view.draw(cam)
    
    for fg in self.foreground_views:
      fg.draw(cam)
      
    #print "TOTAL tiles drawn:", tiles_drawn
      
  def update(self, dt):
    for bg in self.background_views:
      bg.update(dt)
    
    for e in self.entity_views:
      e.update(dt)
      
  def view_for_entity(self, entity):
    for e in self.entity_views:
      if e.entity is entity: return e
    return None
      
  def entity_state_updated_for(self, entity):
    view = self.view_for_entity(entity)
    view.entity_state_updated()
  
  def entity_removed(self, entity):
    entView = self.view_for_entity(entity)
    self.entity_views.remove(entView)

class LayerView(object):
  """docstring for LayerView"""
  def __init__(self, game, layer):
    super(LayerView, self).__init__()
    
    self.game = game
    self.layer = layer
    
  def update(self, dt):
    self.layer.update(dt)

  def draw(self, cam):
    global tiles_drawn
    local_tiles_drawn = 0    
    
    ts = self.layer.tileset
    
    #print "DRAWING", self.layer.name
    #print "  PRE: tiles_drawn", tiles_drawn
    
    # vi försöker få den här positionen inom -tilemap.height > n > tilemap.height
    # fast bara om den repeatar?
    position = euclid.Vector2((-cam.x * self.layer.scroll.x) + self.layer.offset.x + self.layer.startpos.x, (-cam.y * self.layer.scroll.y) + self.layer.offset.y + self.layer.startpos.y)
    
    # Hm, behövs det inte åt andra hållet också?
    if self.layer.repeatx:
      while position.x < -self.layer.tilemap.width:
        position.x += self.layer.tilemap.width
        
    if self.layer.repeaty:
      while position.y < -self.layer.tilemap.height:
        position.y += self.layer.tilemap.height
    
    #print "   draw at pos:",position
    
    glPushMatrix()
    
    # den här slänger ju tilemapens utritning helt rätt. 0,0 hamnar så att säga
    # där den ska hamna. sen är det bara att rita ut hela tilemapen, tjoff!
    glTranslatef(position.x, position.y, 0)
  
    glBindTexture(GL_TEXTURE_2D, ts.texture().data.id)
    
    tm = self.layer.tilemap.map
                            
    glColor3f(self.layer.color.r, self.layer.color.g, self.layer.color.b)
    
    
    # en tilemap kan...
    #  ...repeatas, isåfall ska den ta upp hela skärmen även om den tar 
    
    # när ett lager autoscrollar börjar det hela tiden om när det nått hela sin storlek,
    # så att det inte försvinner ut. auto bör man alltså bara användas tillsammans med repeat
    
    # om tilemapen är scrollad lite åt höger, så att det är tomt till vänster,
    # då ska denna sättas till -tilemap.width så att vi ritar en tilemap längst
    # till vänster som sticker in
    startx = 0
    starty = 0
        
    # räkna ut antalet repeats som behövs för att fylla hela sidan.
    # om tilemapen är flyttad ens en pixel från 0 behövs en till för att fylla ut
    xrepeats = 1
    yrepeats = 1
    if self.layer.repeatx:
      xrepeats = int(math.ceil(20.0 / self.layer.tilemap.width))
      if position.x != 0.0: xrepeats += 1
      if position.x > 0.0: startx = -self.layer.tilemap.width
      #if position.x > 0.0: position.x -= self.layer.tilemap.width
    
    if self.layer.repeaty:
      yrepeats = int(math.ceil(15.0 / self.layer.tilemap.height))
      if position.y != 0.0: yrepeats += 1
      if position.y > 0.0: starty = -self.layer.tilemap.height
      #if position.y > 0.0: position.y -= self.layer.tilemap.height
      
    #print "   tilemap: ", self.layer.tilemap.non_empty_count()
    #print "   xrepeats:", xrepeats
    #print "   yrepeats:", yrepeats
      
      
    #xrepeats = yrepeats = 1
    
    #print "yrepeats: ",yrepeats
                
    glBegin(GL_QUADS)
    
    for yit in range(yrepeats):
      for xit in range(xrepeats):
      
        plusx = xit * self.layer.tilemap.width
        plusy = yit * self.layer.tilemap.height
        
        # här ska vi räkna ut c, ce, r och re igen!
        #if position.x < 0.0:
        #  c = int(-position.x) + 1
        #else:
        #  c = 0
        
        #ce = c + 20
        #if ce > self.layer.tilemap.width: ce = self.layer.tilemap.width
      
        #for y in range(r, re):
        #  for x in range(c, ce):
        for y in range(0, self.layer.tilemap.height):
          #for x in range(c, ce):
          for x in range(0, self.layer.tilemap.width):
      
            drx = startx + plusx + x
            dry = starty + plusy + y
            #drx = position.x + plusx + x
            #dry = position.y + plusy + y
            
            
            tile = tm[y][x]
        
            if tile == 0:
              continue
          
            texcoords = ts.coords_for_tile(tile - 1)

            # kanske är en pytteliten smula snabbare att hämta
            # ut dem såhär. den här metoden är superkritisk allstå.
            a = texcoords.pa
            b = texcoords.pb
            c = texcoords.pc
            d = texcoords.pd
        
            glTexCoord2f(texcoords.pb.x, texcoords.pb.y)
            #glTexCoord2f(0.0, 0.0)
            glVertex2f(drx,     dry)
            glTexCoord2f(texcoords.pa.x, texcoords.pa.y)
            #glTexCoord2f(0.0, 1.0)
            glVertex2f(drx,     dry+1)
            glTexCoord2f(texcoords.pd.x, texcoords.pd.y)
            #glTexCoord2f(1.0, 1.0)
            glVertex2f(drx + 1, dry+1)
            glTexCoord2f(texcoords.pc.x, texcoords.pc.y)
            #glTexCoord2f(1.0, 0.0)
            glVertex2f(drx + 1, dry)
        
            local_tiles_drawn += 1
        
    glEnd()
    
    glPopMatrix()
    
    tiles_drawn += local_tiles_drawn
    
    #print "  POST: i drew", local_tiles_drawn
    #print "  POST: tiles_drawn",tiles_drawn
    
         
class SpriteView(object):
  """docstring for SpriteView"""
  def __init__(self, entity, sprite):
    super(SpriteView, self).__init__()

    # Härifrån kommer positioner och sånt skit
    self.entity = entity
    
    # Här kommer den grafiska datan
    self.sprite = sprite
    
    # Vilket håll spriten tittar. Detta har inget att göra med
    # vilket håll entityn är på väg. Det är dessutom inte nån
    # vektor-riktning utan mer "höger" och "vänster" och kanske "uppåt"
    self.dir = 0
    self.last_view_direction = "right"
    
    self.current_animation = None
    self.current_frame = 0
    self.animation_frameduration = 0 #timer
    
  def set_animation(self, anim_name):
    self.current_animation = self.sprite.animations[anim_name]
    self.current_frame = 0
    
  def draw(self, cam):
    if self.current_animation is None: return
    
    pos = self.entity.pos - self.current_animation.center
    texcoords = self.current_animation.coords_for_frame(self.current_frame)
    w = self.current_animation.size.x
    h = self.current_animation.size.y
    
    a = texcoords.a()
    b = texcoords.b()
    c = texcoords.c()
    d = texcoords.d()
  
    glPushMatrix()
    if self.current_animation.flipx:
      a, d = d, a
      b, c = c, b
    
    if self.current_animation.flipy: 
      a, b = b, a
      d, c = c, d
      
    glTranslatef(-cam.x + pos.x, -cam.y + pos.y, 0)    
        
    glBindTexture(GL_TEXTURE_2D, self.current_animation.texture().data.id)
    
    glColor3f(1., 1., 1.)
    
    glBegin(GL_QUADS)
    
    glTexCoord2f(b.x, b.y)
    glVertex2f(0,0)
    glTexCoord2f(a.x, a.y)
    glVertex2f(0,h)
    glTexCoord2f(d.x, d.y)
    glVertex2f(w,h)
    glTexCoord2f(c.x, c.y)
    glVertex2f(w,0)
    
    glEnd()
    
    glPopMatrix()    
    
    glPushAttrib(GL_ENABLE_BIT)
    glDisable(GL_TEXTURE_2D)
    
    bb = self.entity.boundingbox.translate(self.entity.pos - cam)
    
    glColor3f(1,0,1)
    
    glBegin(GL_LINE_LOOP)
    #glVertex2f(bb.a().x, bb.a().y)
    #glVertex2f(bb.b().x, bb.b().y)
    #glVertex2f(bb.c().x, bb.c().y)
    #glVertex2f(bb.d().x, bb.d().y)
    glEnd()
    
    glPopAttrib()
    
    

  def update(self, dt):
    
    #print "Uppdaterar SPRITE"
    spf = 1.0/self.current_animation.fps
    self.animation_frameduration += dt
    
    if self.animation_frameduration >= spf:
      self.animation_frameduration = 0
      self.current_frame = self.current_frame + 1
      if self.current_frame >= self.current_animation.num_frames:
        self.current_frame = self.current_animation.loopstart
            
      
  def entity_state_updated(self):
    if self.entity.type == 'samus':
      direction = self.last_view_direction
      if "view_left" in self.entity.state:
        direction = "left"
      elif "view_right" in self.entity.state:
        direction = "right"
      self.last_view_direction = direction
    
      action = "stand"
      if "jump" in self.entity.state:
        action = "jump_roll"
      elif "run" in self.entity.state:
        action = "run"
    
      anim = '%s_%s' % (action, direction)
    
      self.set_animation(anim)
    else:
      self.set_animation(self.entity.state[0])
