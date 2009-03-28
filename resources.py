# encoding: utf-8

import demjson
import euclid
import boundingbox

import pyglet
from pyglet.gl import *

textures = {}
sprites = {}    

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


class Texture(object):
  """docstring for Texture"""
  def __init__(self, filename):
    super(Texture, self).__init__()
    
    print "Loading new texture ", filename
    
    self.data = pyglet.image.load(filename).get_texture()
    
    print "texture is ", type(self.data)
    
    glBindTexture(GL_TEXTURE_2D, self.data.id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    
    
class Animation(object):
  def __init__(self, texturename, frames):
      self.fps = 1.0
      self.coords = []
      
      # This is the frame the animation loops back to
      self.loopstart = 0
      
      self.frames = frames
      self.texture = get_texture(texturename)
      
      width = self.texture.data.width
      height = self.texture.data.height
      
      print "loaded texture: ", width, height
      
      print "width", width
      
      bajs = self.texture.data.tex_coords[3]
      print bajs
      
      tjump = (1.0 / self.frames) * bajs
      
      
      print "texjump: ", tjump
      
      for i in range(self.frames):
        mi = euclid.Vector2(i * tjump, 0.0)
        ma = euclid.Vector2(i * tjump + tjump, 1.0)
        self.coords.append( boundingbox.BoundingBox(mi, ma) )
      
      print self.coords
      
class Sprite(object):
  """docstring for Sprite"""
  def __init__(self, name):
    super(Sprite, self).__init__()
    
    print "Creating new sprite ", name
    
    self.animations = {} 
    
    # Öppna datafilen så vi får reda på allt WOHOOOOOOO
    spritedef_file = open("data/sprites/" + name + "/sprite.def")
    
    spritedef = demjson.decode(spritedef_file.read())
    
    self.width = spritedef["size"][0]
    self.height = spritedef["size"][1]
    self.center = euclid.Vector2(spritedef["center"][0], spritedef["center"][1])
    
    animations = spritedef["animations"]
    
    print " animations: (", len(animations), ")"
    
    for k, v in animations.iteritems():    
      texname = "data/sprites/" + name + "/" + v["texture"] + ".png"
      frames = v["frames"]
      
      anim = Animation(texname, frames)
      anim.fps = v["fps"]
      anim.loopstart = v["loopstart"]
      
      self.animations[k] = anim
      
      print " ", k