import moderngl
import pyglet

from domain.renderer import Renderer
from domain.scene import Scene

UPDATES_PER_SECOND = 60.0

class Window(pyglet.window.Window):
    def __init__(self, width: int, height: int, title: str) -> None:
        super().__init__(width, height, title, resizable=True)
        self.gl_context = moderngl.create_context()
        self._scene: Scene | None = None
        self._renderer: Renderer | None = None

    def run(self, scene: Scene, renderer: Renderer) -> None:
        self._scene = scene
        self._renderer = renderer
        self.on_resize(self.width, self.height)
        pyglet.clock.schedule_interval(self._update, 1.0 / UPDATES_PER_SECOND)
        pyglet.app.run()

    def _update(self, delta_seconds: float) -> None:
        self._scene.update(delta_seconds)

    def on_draw(self) -> None:
        if self._renderer is not None:
            self._renderer.render(self._scene)

    def on_resize(self, width: int, height: int) -> None:
        if self._renderer is None:
            return
        framebuffer_width, framebuffer_height = self.get_framebuffer_size()
        self._scene.camera.resize(framebuffer_width, framebuffer_height)
        self._renderer.resize(framebuffer_width, framebuffer_height)
