from demo_scene import build_scene
from infrastructure.opengl.raster_renderer import RasterRenderer
from infrastructure.pyglet_window import Window
from infrastructure.opengl.texture_library import TextureLibrary
from infrastructure.opengl.hitbox_overlay import HitboxOverlay

WIDTH, HEIGHT = 800, 600


def main() -> None:
    window = Window(WIDTH, HEIGHT, "Franco Castellani y Joaquin Martinez")
    scene = build_scene(WIDTH / HEIGHT)
    textures = TextureLibrary(window.gl_context)
    renderer = RasterRenderer(window.gl_context, textures)
    overlay = HitboxOverlay(window.gl_context)
    window.run(scene, renderer, overlay)


if __name__ == "__main__":
    main()
