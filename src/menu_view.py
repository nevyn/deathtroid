from pyglet.gl import *
import network

class MenuScreen(object):
  def __init__(self, controller):
    """docstring for __init"""
    super(MenuScreen, self).__init__()
    self.controller = controller
    self.window = controller.window
    self.init()
    
  def init(self):
    pass
    
  def draw(self):
    pass
    
  def enter(self):
    pass
        
  def exit(self):
    pass
    
  def keyboard_event(self, action):
    pass
    
  def mouse_pressed(self, x, y):
    pass
  
  def mouse_moved(self, x, y):
    pass
  
class NameScreen(MenuScreen):
  def init(self):
    # Enter name
    self.enter_name_image = pyglet.image.load('menu/enter_name.png')

    document1 = pyglet.text.document.FormattedDocument("Samus")
    document1.set_style(0, 5, dict(color=(255, 255, 255, 255)))
    self.enter_name_layout = pyglet.text.layout.IncrementalTextLayout(document1, 100, 20)
    self.enter_name_layout.anchor_x="center"
    self.enter_name_layout.view_x = 0
    self.enter_name_layout.x = 320
    self.enter_name_layout.y = 220
    
    self.caret1 = pyglet.text.caret.Caret(self.enter_name_layout, color=(1, 1, 1))
    self.caret1.visible = True
    self.caret1.position = len(document1.text)
    
  def enter(self):
    self.window.push_handlers(self.caret1)

  def exit(self):
    self.window.remove_handlers(self.caret1)
    
  def draw(self):
    self.enter_name_image.blit(320-(self.enter_name_image.width/2),280)
    self.enter_name_layout.draw()
    
  def keyboard_event(self, action):
    if action == "pressed_enter":
      self.controller.set_player_name(self.enter_name_layout.document.text)
      self.current_state = "server_or_client"
      self.controller.change_state("server_or_client")

    
class ServerClientScreen(MenuScreen):
  """docstring for ClassName"""
  def init(self):
     # Server or client
    self.sc_server = pyglet.image.load('menu/server.png')
    self.sc_server_red = pyglet.image.load('menu/server_red.png')
    self.sc_client = pyglet.image.load('menu/client.png')
    self.sc_client_red = pyglet.image.load('menu/client_red.png')
    self.server_x = 320-(self.sc_server.width/2)
    self.server_y = 240+10
    self.client_x = 320-(self.sc_client.width/2)
    self.client_y = 240-10-(self.sc_client.height)

    self.current_server_img = self.sc_server
    self.current_client_img = self.sc_client
  
  def draw(self):
    self.current_server_img.blit(self.server_x, self.server_y)
    self.current_client_img.blit(self.client_x, self.client_y)
    
  def mouse_pressed(self, x, y):
    if x > self.server_x and x < (self.server_x+self.sc_server.width) and y > self.server_y and y < (self.server_y+self.sc_server.height):
      self.current_state = "start_game"
      self.controller.set_server_or_client("server")
      self.controller.change_state("start_game")
    elif x > self.client_x and x < (self.client_x+self.sc_client.width) and y > self.client_y and y < (self.client_y+self.sc_client.height):
      self.controller.set_server_or_client("client")
      self.controller.change_state("enter_host")

  def mouse_moved(self, x, y):
    if x > self.server_x and x < (self.server_x+self.sc_server.width) and y > self.server_y and y < (self.server_y+self.sc_server.height):
      self.highlight_server_button(True)
    else:
      self.highlight_server_button(False)

    if x > self.client_x and x < (self.client_x+self.sc_client.width) and y > self.client_y and y < (self.client_y+self.sc_client.height):
      self.highlight_client_button(True)
    else:
      self.highlight_client_button(False)

  
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

    
class EnterHostScreen(MenuScreen):
  def init(self):
    # Enter host
    self.enter_host_image = pyglet.image.load('menu/enter_host.png')

    self.document2 = pyglet.text.document.FormattedDocument("localhost")
    self.document2.set_style(0, 9, dict(color=(255, 255, 255, 255)))
    self.enter_host_layout = pyglet.text.layout.IncrementalTextLayout(self.document2, 100, 20)
    self.enter_host_layout.anchor_x="center"
    self.enter_host_layout.view_x = 0
    self.enter_host_layout.x = 320
    self.enter_host_layout.y = 220
    
    self.caret2 = pyglet.text.caret.Caret(self.enter_host_layout, color=(1, 1, 1))
    self.caret2.visible = True
    self.caret2.position = len(self.document2.text)
    

  def draw(self):
    self.enter_host_image.blit(320-(self.enter_host_image.width/2),280)
    self.enter_host_layout.draw()
    
  def enter(self):
    self.window.push_handlers(self.caret2)

  def exit(self):
    self.window.remove_handlers(self.caret2)
    
  def keyboard_event(self, action):
    if action == "pressed_enter":
      self.controller.set_host(self.enter_host_layout.document.text)
      self.current_state = "start_game"
      self.controller.change_state("start_game")


class BrowseScreen(MenuScreen):
  def init(self):
    self.document = pyglet.text.decode_html("<b>Server Browser</b><br><i>Voxar</i> 2 players")
    self.document.set_style(0, 1000000000000, dict(color=(255, 255, 255, 255)))
    self.layout = pyglet.text.layout.IncrementalTextLayout(self.document, 640, 480, True)
    
    self.games = {}
    self.update_text()
#    self.layout.anchor_x = "left"
#    self.layout.view_x = 0
#    self.layout.x = 320
#    self.layout.y = 220
    
  def update_text(self):
    html = """<b>Server Browser</b><br>
    <table><tr>
      <th>Game name</th><th>Host</th>
    </tr>
    <tr>
      <td>Voxars</td><td>my.ip.com</td>
    </tr></table>
    <a href="hej hej">hej</a>
    """
    self.document = pyglet.text.decode_html(html)
    self.document.set_style(0, 1000000000000, dict(color=(255, 255, 255, 255)))
    
    self.layout.document = self.document

  def draw(self):
    self.layout.draw()
    
  def enter(self):
    #self.browser = network.startBrowsing(self)
    pass

  def exit(self):
    pass
    
  def keyboard_event(self, action):
    if action == "pressed_enter":
      pass
      
  def gameAdded(self, name, gameinfo):
    self.games[name] = gameinfo
    self.update_text()

  def gameRemoved(self, name, host, port):
    del self.games[name]
    self.update_text()
