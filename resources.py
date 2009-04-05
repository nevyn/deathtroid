# encoding: utf-8

import demjson
import euclid
import boundingbox

import pyglet
from pyglet.gl import *
from pyglet import clock


############# Graphics

textures = {}
sprites = {} 
tilesets = {}

def get_texture(name):
  if name in textures: return textures[name]
  
  tex = Texture(name)
  textures[name] = tex
  return tex

def get_sprite(name):
  if name in sprites: return sprites[name]

  spr = Sprite(name)
  sprites[name] = spr
  return spr
  
def get_tileset(name):
  if name in tilesets: return tilesets[name]
  
  ts = Tileset(name)
  tilesets[name] = ts
  return ts

def update(dt):
  for t, v in tilesets.items():
    v.update(dt)

class Texture(object):
  """docstring for Texture"""
  def __init__(self, filename):
    super(Texture, self).__init__()
    
    print "Loading new texture", filename
    
    self.data = pyglet.image.load(filename).get_texture()
    
    glBindTexture(GL_TEXTURE_2D, self.data.id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    
  def bind(self):
    glBindTexture(GL_TEXTURE_2D, self.data.id)
    
    
class TextureStrip(object):
  """Texture strip"""
  def __init__(self, texturename, num_parts):
    super(TextureStrip, self).__init__()
    
    self.texture = get_texture(texturename)
    self.coords = []
    self.num_parts = num_parts
    
    width = self.texture.data.width
    height = self.texture.data.height
          
    # Real width of texture, pyglet always creates a texture
    # with power-of-two sides internally. Use this to 
    # calculate UV for each part.
    real_w = self.texture.data.tex_coords[3]
    real_h = self.texture.data.tex_coords[7]
    tjump = (1.0 / self.num_parts) * real_w
    
    for i in range(self.num_parts):
      mi = euclid.Vector2(i * tjump, 0.0)
      ma = euclid.Vector2(i * tjump + tjump, real_h)
      self.coords.append( boundingbox.BoundingBox(mi, ma) )
      print self.coords[i]

# Basically just a thin wrapper around texturestrip
# that adds animation logic (fps, looping)
class Animation(object):
  #def __init__(self, texturename, frames, fps, loopstart):
  def __init__(self, texturename, data):
    self.size = euclid.Vector2(data["size"][0], data["size"][1])
    self.center = euclid.Vector2(data["center"][0], data["center"][1])
    
    self.fps = data["fps"]
    self.loopstart = data["loopstart"]
    self.num_frames = data["frames"]
    
    self.flipx = False
    self.flipy = False
    
    if "flip" in data:
      self.flipx = data["flip"][0]
      self.flipy = data["flip"][1]
    
    self.strip = TextureStrip(texturename, self.num_frames)
      
  def coords_for_frame(self, frame):
    return self.strip.coords[frame]
    
  def texture(self):
    return self.strip.texture

class Sprite(object):
  """docstring for Sprite"""
  def __init__(self, name):
    super(Sprite, self).__init__()
    
    print "Creating new sprite", name
    
    # List of TextureStrips
    self.animations = {}
    
    spritedef_file = open("data/sprites/" + name + "/sprite.def")
    
    spritedef = demjson.decode(spritedef_file.read())
    
    #self.width = spritedef["size"][0]
    #self.height = spritedef["size"][1]
    #self.center = euclid.Vector2(spritedef["center"][0], spritedef["center"][1])
    
    animations = spritedef["animations"]
    
    print " animations: (", len(animations), ")"
    
    for k, v in animations.iteritems():    
      texname = "data/sprites/" + name + "/" + v["texture"] + ".png"
            
      #anim = Animation(texname, v["frames"], v["fps"], v["loopstart"])
      anim = Animation(texname, v)
      self.animations[k] = anim
      
      print " ", k
      
      
class Tile(object):
  """docstring for Tile"""
  def __init__(self, start, length, fps):
    super(Tile, self).__init__()
    
    self.start = start
    self.length = length
    self.fps = fps
    
    self.current = self.start

class Tileset(object):
  """docstring for Tileset"""
  def __init__(self, name):
    super(Tileset, self).__init__()
    
    # This is indexed by tilemaps
    self.tiles = []
    
    tiles_def_file = open("data/tilesets/" + name + ".tiles")
    tiles_def = demjson.decode(tiles_def_file.read())
    
    for t in tiles_def:
      self.tiles.append( Tile(t[0], t[1], t[2]) )
      
    self.strip = TextureStrip("data/tilesets/" + name + ".png", len(self.tiles))
    
    print "Number of tiles: ",len(self.tiles)
    
  def texture(self):
    return self.strip.texture
    
  def coords_for_tile(self, tile):
    return self.strip.coords[self.tiles[tile].current]
    
  def update(self, dt):        
    for t in self.tiles:
      t.current += 1
      if t.current >= t.start + t.length:
        t.current = t.start


########### Sounds

cam = euclid.Vector2(0,0)

midOfScreen = euclid.Vector2(20./2, 16./2)

def cam_changed(newCam):
  cam.x = newCam.x
  cam.y = newCam.y
  
  midCam = cam + midOfScreen
  
  pyglet.media.listener.forward_orientation = (0., 0., 1.)
  pyglet.media.listener.up_orientation      = (0., -2., 0.)
  pyglet.media.listener.position = (midCam.x/4., midCam.y/4., -2.)

sounds = {}

def get_sound(name):
  if name in sounds: return sounds[name]
  
  sound = Sound(name)
  sounds[name] = sound
  return sound


class Sound(object):
  """Sound resource."""
  def __init__(self, name):
    super(Sound, self).__init__()
    self.name = name
    
    self.mediaSource = pyglet.media.load("data/sounds/"+name+".wav", streaming = False)
  
  def voice(self, **opts):
    player = pyglet.media.Player()
    player.queue(self.mediaSource)
    return Voice(player, **opts)
  
  def voiceAt(self, where, **opts):
    voice = self.voice(**opts)
    voice.position = euclid.Vector2(where.x, where.y)
    return voice
  
  def voiceFollowing(self, entity, **opts):
    voice = self.playAt(entity.pos, **opts)
    voice.follow(entity)
    return voice
  
  def play(self, **opts):
    return self.voice(**opts).play()
    
  def playAt(self, where, **opts):
    return self.voiceAt(where, **opts).play()
    
  def playFollowing(self, entity, **opts):
    return self.voiceFollowing(entity, **opts).play()

class Voice(object):
  """A single, currently playing sound."""
  def __init__(self, player, volume = 1.0, loop = False, callback = None):
    """'player' is a pyglet.media.Player, not a model.Player"""
    super(Voice, self).__init__()
    self.player = player
    self.player.on_eos = self.stream_ended
    self.old_eos_action = self.player.eos_action
    self.entity = None
    self._callback = None
    
    self.volume = volume
    self.loop = loop
    self.callback = callback
    
  def schedule_update_if_needed(self):
    clock.unschedule(self.update)
    if self._callback or self.entity:
      clock.schedule_interval_soft(self.update, 1./10.)
      
  
  def position():
    doc = "Position of the voice in the world. Don't use the underlying player's position, that one is in another space."
    def fget(self):
      return euclid.Vector2(self.player.position[0]*4., self.player.position[1]*4.)
    def fset(self, vec):
      self.player.position = (vec.x/4., vec.y/4, 0.)
    return locals()
  position = property(**position())
  
  def callback():
    doc = "A callback that is called with 10hz during sound play"
    def fget(self):
      return self._callback
    def fset(self, value):
      self._callback = value
      self.schedule_update_if_needed()
    def fdel(self):
      del self._callback
    return locals()
  callback = property(**callback())
  
  def volume():
    doc = "Sound volume."
    def fget(self):
      return self.player.volume
    def fset(self, value):
      self.player.volume = value
    return locals()
  volume = property(**volume())

  def follow(self, entity):
    self.entity = entity
    self.schedule_update_if_needed()
    return self
  
  def stream_ended(self):
    if self.player.eos_action != pyglet.media.Player.EOS_LOOP:
      self.stop()
  
  def play(self):
    self.player.play()
    return self
  
  def stop(self):
    clock.unschedule(self.update)
    self.player.pause()
    return self
  
  def update(self, dt):
    if self.entity:
      if self.entity.removed:
        self.stop()
      else:
        self.position = self.entity.pos
    
    if self.callback:
      self.callback(self)
    
  
  def loop():
      doc = "Whether to loop this voice. Bool."
      def fget(self):
          return self.player.eos_action == pyglet.media.Player.EOS_LOOP
      def fset(self, value):
        if value:
          self.old_eos_action = self.player.eos_action
          self.player.eos_action = pyglet.media.Player.EOS_LOOP
        else:
          self.player.eos_action = self.old_eos_action
      return locals()
  loop = property(**loop())
  

