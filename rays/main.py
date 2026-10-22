from demo_scene import build_scene
from domain.renderer import Renderer
from infrastructure.opengl.cpu_raytrace_renderer import CpuRaytraceRenderer
from infrastructure.opengl.hitbox_overlay import HitboxOverlay
from infrastructure.opengl.raster_renderer import RasterRenderer
from infrastructure.opengl.texture_library import TextureLibrary
from infrastructure.pyglet_window import Window

WIDTH, HEIGHT = 800, 600
SCENE_TYPE = "cpu"  # "raster" o "cpu"


def create_renderer(window: Window) -> Renderer:
    if SCENE_TYPE == "cpu":
        return CpuRaytraceRenderer(window.gl_context)
    return RasterRenderer(window.gl_context, TextureLibrary(window.gl_context))


def main() -> None:
    window = Window(WIDTH, HEIGHT, "Franco Castellani y Joaquin Martinez")
    scene = build_scene(WIDTH / HEIGHT)
    renderer = create_renderer(window)
    overlay = HitboxOverlay(window.gl_context)
    window.run(scene, renderer, overlay)


if __name__ == "__main__":
    main()
