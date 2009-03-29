from pyglet.gl import *

class MenuView(object):

  def __init__(self, window, state, controller):
    super(MenuView, self).__init__()
    
    self.window = window
    self.current_state = state
    self.controller = controller
    
    # Enter name
    self.enter_name_image = pyglet.image.load('data/menu/enter_name.png')

    document1 = pyglet.text.document.FormattedDocument("Samus")
    document1.set_style(0, 5, dict(color=(255, 255, 255, 255)))
    self.enter_name_layout = pyglet.text.layout.IncrementalTextLayout(document1, 100, 20)
    self.enter_name_layout.anchor_x="center"
    self.enter_name_layout.view_x = 0
    self.enter_name_layout.x = 320
    self.enter_name_layout.y = 220
    
    caret1 = pyglet.text.caret.Caret(self.enter_name_layout, color=(1, 1, 1))
    caret1.visible = True
    caret1.position = len(document1.text)
    self.window.push_handlers(caret1)
    
    
    # Server or client
    self.sc_server = pyglet.image.load('data/menu/server.png')
    self.sc_server_red = pyglet.image.load('data/menu/server_red.png')
    self.sc_client = pyglet.image.load('data/menu/client.png')
    self.sc_client_red = pyglet.image.load('data/menu/client_red.png')
    self.server_x = 320-(self.sc_server.width/2)
    self.server_y = 240+10
    self.client_x = 320-(self.sc_client.width/2)
    self.client_y = 240-10-(self.sc_client.height)
    
    self.current_server_img = self.sc_server
    self.current_client_img = self.sc_client
    
    
    
    # Enter host
    self.enter_host_image = pyglet.image.load('data/menu/enter_host.png')

    self.document2 = pyglet.text.document.FormattedDocument("localhost")
    self.document2.set_style(0, 9, dict(color=(255, 255, 255, 255)))
    self.enter_host_layout = pyglet.text.layout.IncrementalTextLayout(self.document2, 100, 20)
    self.enter_host_layout.anchor_x="center"
    self.enter_host_layout.view_x = 0
    self.enter_host_layout.x = 320
    self.enter_host_layout.y = 220



  def draw(self):

    if self.current_state == "enter_name":
      self.enter_name_image.blit(320-(self.enter_name_image.width/2),280)
      self.enter_name_layout.draw()
      
    elif self.current_state == "server_or_client":
      self.current_server_img.blit(self.server_x, self.server_y)
      self.current_client_img.blit(self.client_x, self.client_y)
      
    elif self.current_state == "enter_host":
      self.enter_host_image.blit(320-(self.enter_host_image.width/2),280)
      self.enter_host_layout.draw()
      
  
  def highlight_server_button(self, highlight):
    
    if highlight:
      self.current_server_img = self.sc_server_red
    else:
      self.current_server_img = self.sc_server
      
      
  def highlight_client_button(self, highlight):

    if highlight == True:
      self.current_client_img = self.sc_client_red
    else:
      self.current_client_img = self.sc_client
      
  
  def init_state(self, state):
    
    if state == "enter_host":
      caret2 = pyglet.text.caret.Caret(self.enter_host_layout, color=(1, 1, 1))
      caret2.visible = True
      caret2.position = len(self.document2.text)
      self.window.push_handlers(caret2)
      
  def keyboard_event(self, action):

    if self.current_state == "enter_name":
      if action == "pressed_enter":
        self.controller.set_player_name(self.enter_name_layout.document.text)
        self.current_state = "server_or_client"
        self.init_state("server_or_client")
        self.controller.change_state("server_or_client")
        
    elif self.current_state == "enter_host":
      if action == "pressed_enter":
        self.controller.set_host(self.enter_host_layout.document.text)
        self.current_state = "start_game"
        self.init_state("start_game")
        self.controller.change_state("start_game")
      
      
  def mouse_pressed(self, x, y):

    if self.current_state == "server_or_client":

      if x > self.server_x and x < (self.server_x+self.sc_server.width) and y > self.server_y and y < (self.server_y+self.sc_server.height):
        self.current_state = "start_game"
        self.controller.set_server_or_client("server")
        self.controller.change_state("start_game")

      elif x > self.client_x and x < (self.client_x+self.sc_client.width) and y > self.client_y and y < (self.client_y+self.sc_client.height):
        self.current_state = "enter_host"
        self.init_state("enter_host")
        self.controller.set_server_or_client("client")
        self.controller.change_state("enter_host")


  def mouse_moved(self, x, y):

    if self.current_state == "server_or_client":

      if x > self.server_x and x < (self.server_x+self.sc_server.width) and y > self.server_y and y < (self.server_y+self.sc_server.height):
          self.highlight_server_button(True)

      else:
        self.highlight_server_button(False)

      if x > self.client_x and x < (self.client_x+self.sc_client.width) and y > self.client_y and y < (self.client_y+self.sc_client.height):
        self.highlight_client_button(True)

      else:
        self.highlight_client_button(False)
    
      
    