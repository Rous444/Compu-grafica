import moderngl

from domain.scene import Scene
from infrastructure.opengl.gpu_scene import GpuScene
from infrastructure.opengl.screen_quad import ScreenQuad
from infrastructure.opengl.shader_loader import load_compute, load_program
from infrastructure.opengl.texture_library import TextureLibrary

WORK_GROUP_SIZE = 8
ACCUMULATION_IMAGE_UNIT = 0
OBJECTS_BINDING = 1
PREVIOUS_FRAME_UNIT = 2
MAX_BOUNCES = 4
SAMPLES_PER_FRAME = 4


def _group_count(pixels: int) -> int:
    return (pixels + WORK_GROUP_SIZE - 1) // WORK_GROUP_SIZE


class Accumulation:
    """Cuenta los frames acumulados y vuelve a empezar cuando cambia la escena o la cámara."""

    def __init__(self) -> None:
        self.frame_index = 0
        self._signature = b""

    def advance(self, scene_bytes: bytes, camera_bytes: bytes) -> None:
        signature = scene_bytes + camera_bytes
        if signature != self._signature:
            self._signature = signature
            self.frame_index = 0
        else:
            self.frame_index += 1

    def restart(self) -> None:
        self._signature = b""
        self.frame_index = 0

    @property
    def sample_count(self) -> int:
        return (self.frame_index + 1) * SAMPLES_PER_FRAME


class ComputePathtraceRenderer:
    """Pathtracing en un compute shader: cada frame suma muestras al promedio de cada píxel."""

    def __init__(self, context: moderngl.Context, textures: TextureLibrary, scene: Scene) -> None:
        self._context = context
        self._shader = load_compute(context, "pathtrace")
        self._gpu_scene = GpuScene(context, textures, scene)
        self._screen = ScreenQuad(context)
        self._accumulation = Accumulation()
        self._image: moderngl.Texture | None = None
        self._size = (1, 1)

    @property
    def sample_count(self) -> int:
        return self._accumulation.sample_count

    def resize(self, framebuffer_width: int, framebuffer_height: int) -> None:
        self._context.viewport = (0, 0, framebuffer_width, framebuffer_height)
        self._size = (max(1, framebuffer_width), max(1, framebuffer_height))
        if self._image is not None:
            self._image.release()
        self._image = self._context.texture(self._size, 4, dtype="f4")
        self._accumulation.restart()

    def render(self, scene: Scene) -> None:
        width, height = self._size
        self._gpu_scene.upload(scene)
        self._accumulation.advance(self._gpu_scene.last_upload, scene.camera.view_matrix().to_bytes())
        self._gpu_scene.objects_buffer.bind_to_storage_buffer(OBJECTS_BINDING)
        self._gpu_scene.apply(self._shader, scene, width / height)
        self._shader["u_max_bounces"] = MAX_BOUNCES
        self._shader["u_frame_index"] = self._accumulation.frame_index
        self._shader["u_samples_per_frame"] = SAMPLES_PER_FRAME
        self._image.bind_to_image(ACCUMULATION_IMAGE_UNIT, read=True, write=True)
        self._shader.run(_group_count(width), _group_count(height))
        self._context.memory_barrier()
        self._screen.draw(self._image)


class FragmentPathtraceRenderer:
    """Ping-pong: cada frame lee el promedio anterior de una textura y escribe el nuevo en la otra."""

    def __init__(self, context: moderngl.Context, textures: TextureLibrary, scene: Scene) -> None:
        self._context = context
        self._program = load_program(context, "screen", "pathtrace_fragment")
        self._program["SceneObjects"].binding = OBJECTS_BINDING
        self._vertex_array = context.vertex_array(self._program, [])
        self._gpu_scene = GpuScene(context, textures, scene)
        self._screen = ScreenQuad(context)
        self._accumulation = Accumulation()
        self._targets: list[tuple[moderngl.Texture, moderngl.Framebuffer]] = []
        self._size = (1, 1)

    @property
    def sample_count(self) -> int:
        return self._accumulation.sample_count

    def resize(self, framebuffer_width: int, framebuffer_height: int) -> None:
        self._size = (max(1, framebuffer_width), max(1, framebuffer_height))
        for texture, framebuffer in self._targets:
            framebuffer.release()
            texture.release()
        self._targets = []
        for _ in range(2):
            texture = self._context.texture(self._size, 4, dtype="f4")
            self._targets.append((texture, self._context.framebuffer(color_attachments=[texture])))
        self._accumulation.restart()

    def render(self, scene: Scene) -> None:
        width, height = self._size
        screen = self._context.fbo   # el framebuffer de la ventana, para volver a él al final
        self._gpu_scene.upload(scene)
        self._accumulation.advance(self._gpu_scene.last_upload, scene.camera.view_matrix().to_bytes())
        (previous_texture, _), (current_texture, current_framebuffer) = self._targets

        self._gpu_scene.objects_buffer.bind_to_uniform_block(OBJECTS_BINDING)
        self._gpu_scene.apply(self._program, scene, width / height)
        previous_texture.use(location=PREVIOUS_FRAME_UNIT)
        self._program["u_previous"] = PREVIOUS_FRAME_UNIT
        self._program["u_max_bounces"] = MAX_BOUNCES
        self._program["u_frame_index"] = self._accumulation.frame_index
        self._program["u_samples_per_frame"] = SAMPLES_PER_FRAME
        self._program["u_resolution"] = (float(width), float(height))

        # 1. Calculamos el nuevo promedio en la textura "actual".
        current_framebuffer.use()
        self._context.disable(moderngl.DEPTH_TEST)
        self._vertex_array.render(mode=moderngl.TRIANGLE_STRIP, vertices=4)

        # 2. Lo mostramos en la ventana.
        screen.use()
        self._context.viewport = (0, 0, width, height)
        self._screen.draw(current_texture)

        # 3. Intercambiamos: la actual pasa a ser la anterior del próximo frame.
        self._targets.reverse()
