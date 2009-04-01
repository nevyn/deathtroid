import menu_view
from pyglet.gl import *



class MenuController(object):
  
  def __init__(self, window):
    super(MenuController, self).__init__()
    
    self.current_state = "enter_name"
    self.view = menu_view.MenuView(window, self.current_state, self)
    
    
    self.player_name = "Samus"
    self.server_or_client ="server"
    self.host = "localhost"
        
    
  def update(self, dt):        
    pass
    
    
  def draw(self):
    self.view.draw()
    
    
  def resize(self, width, height):
    
    glViewport(0, 0, width, height)
    glMatrixMode(gl.GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, 640, 0, 480, -1, 1)
    glMatrixMode(gl.GL_MODELVIEW)
    
  
  def set_player_name(self, name):
    temp = name.partition("\n")
    self.player_name = temp[0]
    
  def set_server_or_client(self, sc):
    self.server_or_client = sc
    
  def set_host(self, host):
    temp = host.partition("\n")
    self.host = temp[0]
    
  def change_state(self, state):
    self.current_state = state
    
    if state == "start_game":
      print "Player name: ", self.player_name
      print "Server of client: ", self.server_or_client
      if self.server_or_client == "client":
        print "Host: ", self.host
    else:
      self.view.goto(state)

  def keyboard_event(self, action):
    
    self.view.keyboard_event(action)
        
  
  def mouse_pressed(self, x, y):
    
    print "mouse pressed ", x, " ", y
    self.view.mouse_pressed(x, y)
        
        
  def mouse_moved(self, x, y):
        
    self.view.mouse_moved(x, y)
    
    