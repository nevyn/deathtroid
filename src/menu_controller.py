import menu_view
from pyglet.gl import *


class MenuController(object):
  
  def __init__(self, window):
    super(MenuController, self).__init__()
    self.window = window
    self.current_state = "enter_name"
    self.current_state = "browse_host"
#    self.view = menu_view.MenuView(window, self.current_state, self)
    
    self.queue = []
    self.player_name = "Samus"
    self.server_or_client ="server"
    self.host = "localhost"
    
    self.screens = {
      "enter_name":       menu_view.NameScreen(self),
      "server_or_client": menu_view.ServerClientScreen(self),
      "enter_host":       menu_view.EnterHostScreen(self),
      "browse_host":      menu_view.BrowseScreen(self)
    }
    
    self.current_screen = None
    self.change_state(self.current_state)
        
  def push_screen(self, name):
    self.queue.append(name)
    self.change_screen(name)
    
  def pop_screen(self):
    if len(self.queue) > 1:
      screen = self.queue[-2]
      self.queue = self.queue[:-1]
      self.change_screen(screen)
      
  def activate(self, screen):
    if self.current_screen:
      self.current_screen.exit()

    self.current_screen = screen

    if self.current_screen:
      self.current_screen.enter()
    
  def change_screen(self, name):
    self.activate(self.screens[name])

  def update(self, dt):        
    pass
    
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
        self.window.start_game("client", self.player_name, self.host)
      else:
        self.window.start_game("both", self.player_name)
    else:
      self.push_screen(state)

  def draw(self):
    self.current_screen.draw()  

  def keyboard_event(self, action):
    if action == "pressed_escape":
      self.pop_screen()
    else:
      self.current_screen.keyboard_event(action)

  def mouse_pressed(self, x, y):
    self.current_screen.mouse_pressed(x, y)

  def mouse_moved(self, x, y):
    self.current_screen.mouse_moved(x, y)
    
    