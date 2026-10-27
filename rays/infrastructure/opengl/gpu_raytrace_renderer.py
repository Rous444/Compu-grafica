import moderngl

from domain.scene import Scene
from infrastructure.opengl.gpu_scene import GpuScene
from infrastructure.opengl.screen_quad import ScreenQuad
from infrastructure.opengl.shader_loader import load_compute, load_program
from infrastructure.opengl.texture_library import TextureLibrary

WORK_GROUP_SIZE = 8
OUTPUT_IMAGE_UNIT = 0
OBJECTS_BINDING = 1


def _group_count(pixels: int) -> int:
    """Cantidad de work groups de 8 que hacen falta para cubrir los píxeles (redondeando hacia arriba)."""
    return (pixels + WORK_GROUP_SIZE - 1) // WORK_GROUP_SIZE

class ComputeRaytraceRenderer:
    """Raytracing en un compute shader: una invocación por píxel, organizadas en work groups de 8 x 8."""

    def __init__(self, context: moderngl.Context, textures: TextureLibrary, scene: Scene) -> None:
        self._context = context
        self._shader = load_compute(context, "raytrace")
        self._gpu_scene = GpuScene(context, textures, scene)
        self._screen = ScreenQuad(context)
        self._output: moderngl.Texture | None = None
        self._size = (1, 1)
    
    def resize(self, framebuffer_width: int, framebuffer_height: int) -> None:
        self._context.viewport = (0, 0, framebuffer_width, framebuffer_height)
        self._size = (max(1, framebuffer_width), max(1, framebuffer_height))
        if self._output is not None:
            self._output.release()
        self._output = self._context.texture(self._size, 4)

    def render(self, scene: Scene) -> None:
        width, height = self._size
        self._gpu_scene.apply(self._shader, scene, width / height)
        self._gpu_scene.upload(scene)
        self._gpu_scene.objects_buffer.bind_to_storage_buffer(OBJECTS_BINDING)
        self._output.bind_to_image(OUTPUT_IMAGE_UNIT, read=False, write=True)
        self._shader.run(_group_count(width), _group_count(height))
        # Esperamos a que el compute shader termine de escribir antes de leer la imagen.
        self._context.memory_barrier()
        self._screen.draw(self._output)

class FragmentRaytraceRenderer:
    """El mismo trazado en un fragment shader sobre un rectángulo de pantalla completa (OpenGL 3.3)."""

    def __init__(self, context: moderngl.Context) -> None:
        self._context = context
        self._program = load_program(context, "screen", "raytrace_fragment")
        self._vertex_array = context.vertex_array(self._program, [])
        self._gpu_scene = GpuScene()
        self._size = (1, 1)
        self._program["SceneObjects"].binding = OBJECTS_BINDING

    def resize(self, framebuffer_width: int, framebuffer_height: int) -> None:
        self._context.viewport = (0, 0, framebuffer_width, framebuffer_height)
        self._size = (max(1, framebuffer_width), max(1, framebuffer_height))

    def render(self, scene: Scene) -> None:
        width, height = self._size
        self._gpu_scene.apply(self._program, scene, width / height)
        self._gpu_scene.upload(scene)
        self._gpu_scene.objects_buffer.bind_to_uniform_block(OBJECTS_BINDING)
        self._context.disable(moderngl.DEPTH_TEST)
        self._vertex_array.render(mode=moderngl.TRIANGLE_STRIP, vertices=4)

        