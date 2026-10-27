from demo_scene import build_scene
from domain.renderer import Renderer
from infrastructure.opengl.cpu_raytrace_renderer import CpuRaytraceRenderer
from infrastructure.opengl.hitbox_overlay import HitboxOverlay
from infrastructure.opengl.raster_renderer import RasterRenderer
from infrastructure.opengl.texture_library import TextureLibrary
from infrastructure.pyglet_window import Window
from domain.scene import Scene
from infrastructure.opengl.gpu_raytrace_renderer import ComputeRaytraceRenderer, FragmentRaytraceRenderer

SCENE_TYPE = "gpu"  # "raster", "cpu" o "gpu"
COMPUTE_SHADER_VERSION = 430

WIDTH, HEIGHT = 800, 600
#SCENE_TYPE = "raster"  # "raster" o "cpu"

def create_gpu_renderer(window: Window, scene: Scene) -> Renderer:
    """Compute shader si la placa lo soporta (OpenGL 4.3); si no, fragment shader (macOS)."""
    context = window.gl_context
    textures = TextureLibrary(context)
    if context.version_code >= COMPUTE_SHADER_VERSION:
        return ComputeRaytraceRenderer(context, textures, scene)
    print(f"OpenGL {context.version_code} no tiene compute shaders: usamos el fragment shader.")
    return FragmentRaytraceRenderer(context, textures, scene)

def create_renderer(window: Window, scene: Scene) -> Renderer:
    if SCENE_TYPE == "gpu":
        return create_gpu_renderer(window, scene)
    if SCENE_TYPE == "cpu":
        return CpuRaytraceRenderer(window.gl_context)
    return RasterRenderer(window.gl_context, TextureLibrary(window.gl_context))

def main() -> None:
    window = Window(WIDTH, HEIGHT, "Franco Castellani y Joaquin Martinez")
    scene = build_scene(WIDTH / HEIGHT)
    renderer = create_renderer(window, scene)
    overlay = HitboxOverlay(window.gl_context)
    window.run(scene, renderer, overlay)


if __name__ == "__main__":
    main()
