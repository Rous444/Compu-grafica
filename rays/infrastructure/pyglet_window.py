import moderngl
import pyglet

from pyglet.window import key, mouse

from domain.renderer import ProgressiveRenderer, Renderer
from domain.scene import Scene

TITLE_REFRESH_SECONDS = 0.25
UPDATES_PER_SECOND = 60.0
OPENGL_VERSIONS = ((4, 3), (4, 1), (3, 3))


def _best_config() -> pyglet.gl.Config | None:
    """Pide OpenGL 4.3 (compute shaders). macOS llega hasta 4.1, así que probamos versiones menores."""
    # En pyglet 2.1 el módulo se llama display; en versiones anteriores, canvas.
    display_module = getattr(pyglet, "display", None) or pyglet.canvas
    screen = display_module.get_display().get_default_screen()
    for major, minor in OPENGL_VERSIONS:
        config = pyglet.gl.Config(major_version=major, minor_version=minor, forward_compatible=True,
                                  depth_size=24, double_buffer=True)
        try:
            screen.get_best_config(config)
            return config
        except pyglet.window.NoSuchConfigException:
            continue
    return None

class Window(pyglet.window.Window):
    def __init__(self, width: int, height: int, title: str) -> None:
        super().__init__(width, height, title, resizable=True, config=_best_config())
        self._scene: Scene | None = None
        self._renderer: Renderer | None = None
        self._base_title = title
        self._overlay: Renderer | None = None
        self.gl_context = moderngl.create_context()
        print(f"OpenGL {self.gl_context.version_code}: {self.gl_context.info['GL_RENDERER']}")

    def _refresh_title(self, _delta_seconds: float = 0.0) -> None:
        parts = [self._base_title]
        if isinstance(self._renderer, ProgressiveRenderer):
            parts.append(f"{self._renderer.sample_count} muestras")
        if self._scene.paused:
            parts.append("PAUSA (espacio)")
        self.set_caption(" | ".join(parts))

    def run(self, scene: Scene, renderer: Renderer, overlay: Renderer) -> None:
        self._scene = scene
        self._renderer = renderer
        self._overlay = overlay
        self.on_resize(self.width, self.height)
        pyglet.clock.schedule_interval(self._update, 1.0 / UPDATES_PER_SECOND)
        if isinstance(renderer, ProgressiveRenderer):
            scene.paused = True  # el pathtracing solo converge con la escena quieta
        pyglet.clock.schedule_interval(self._refresh_title, TITLE_REFRESH_SECONDS)
        pyglet.app.run()

    def _update(self, delta_seconds: float) -> None:
        self._scene.update(delta_seconds)

    def on_draw(self) -> None:
        if self._renderer is not None:
            self._renderer.render(self._scene)
            self._overlay.render(self._scene)

    def on_resize(self, width: int, height: int) -> None:
        if self._renderer is None:
            return
        framebuffer_width, framebuffer_height = self.get_framebuffer_size()
        self._scene.camera.resize(framebuffer_width, framebuffer_height)
        self._renderer.resize(framebuffer_width, framebuffer_height)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button != mouse.LEFT:
            return
        # Pyglet mide el mouse en píxeles desde la esquina inferior izquierda, igual que la v de la cámara.
        ray = self._scene.camera.ray_through(x / self.width, y / self.height)
        found = self._scene.pick(ray)
        if found is None:
            print("Nada bajo el cursor")
            return
        entity, hit = found
        entity.show_hitbox = not entity.show_hitbox
        print(f"Hit: {entity.name} a {hit.distance:.2f} unidades")

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == key.SPACE:
            self._scene.paused = not self._scene.paused
            self._refresh_title()
        else:
            super().on_key_press(symbol, modifiers)
