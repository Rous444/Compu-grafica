from demo_scene import build_scene
from infrastructure.opengl.raster_renderer import RasterRenderer
from infrastructure.pyglet_window import Window

WIDTH, HEIGHT = 800, 600


def main() -> None:
    window = Window(WIDTH, HEIGHT, "Franco")
    scene = build_scene(WIDTH / HEIGHT)
    renderer = RasterRenderer(window.gl_context)
    window.run(scene, renderer)


if __name__ == "__main__":
    main()
