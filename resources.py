# encoding: utf-8

import demjson
import euclid
import boundingbox

import pyglet
from pyglet.gl import *

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
    self.center = euclid.Vector2(data["center"][0], data["size"][1])
    
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
    