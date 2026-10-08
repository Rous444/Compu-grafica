import moderngl
import pyglet


class Window(pyglet.window.Window):
   def __init__(self, width: int, height: int, title: str) -> None:
           super().__init__(width, height, title, resizable=true)
           self.gl_context = moderngl.create_context()

def run(self) -> None:
     pyglet.app.run()
def on_draw(self) -> None:
     self.gl_context.clear(0.2,0.2,0.2)