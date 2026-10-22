from demo_scene import build_scene
from infrastructure.opengl.raster_renderer import RasterRenderer
from infrastructure.pyglet_window import Window
from infrastructure.opengl.texture_library import TextureLibrary

WIDTH, HEIGHT = 800, 600


def main() -> None:
    window = Window(WIDTH, HEIGHT, "Franco Castellani y Joaquin Martinez")
    scene = build_scene(WIDTH / HEIGHT)
    textures = TextureLibrary(window.gl_context)
    renderer = RasterRenderer(window.gl_context, textures)
    window.run(scene, renderer)


if __name__ == "__main__":
    main()
