import moderngl
from pyglm import glm

from domain.intersections import closest_hit
from domain.ray import Ray
from domain.scene import Scene
from infrastructure.opengl.screen_quad import ScreenQuad

DOWNSCALE = 8
SURFACE_OFFSET = 1e-3


class CpuRaytraceRenderer:
    """Raytracing en Python: un rayo por píxel de una imagen chica, que después se estira a la ventana."""

    def __init__(self, context: moderngl.Context) -> None:
        self._context = context
        self._screen = ScreenQuad(context)
        self._size = (1, 1)
        self._pixels = bytearray(3)
        self._texture: moderngl.Texture | None = None

    def resize(self, framebuffer_width: int, framebuffer_height: int) -> None:
        self._context.viewport = (0, 0, framebuffer_width, framebuffer_height)
        width = max(1, framebuffer_width // DOWNSCALE)
        height = max(1, framebuffer_height // DOWNSCALE)
        self._size = (width, height)
        self._pixels = bytearray(width * height * 3)
        if self._texture is not None:
            self._texture.release()
        self._texture = self._context.texture(self._size, 3, bytes(self._pixels))
        self._texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

    def _set_pixel(self, x: int, y: int, color: glm.vec3) -> None:
        """Guarda un color en [0, 1] como 3 bytes en [0, 255]. La fila 0 es la de abajo."""
        color = glm.clamp(color, 0.0, 1.0)
        offset = (y * self._size[0] + x) * 3
        self._pixels[offset:offset + 3] = bytes(int(channel * 255) for channel in color)

    @staticmethod
    def _trace(scene: Scene, ray: Ray) -> glm.vec3:
        found = closest_hit(ray, scene.entities)
        if found is None:
            return scene.sky.color_for(ray.direction)
        entity, hit = found
        to_light = scene.light.to_light()
        shadow_ray = Ray(hit.point + hit.normal * SURFACE_OFFSET, to_light)
        visibility = 0.0 if closest_hit(shadow_ray, scene.entities) else 1.0
        diffuse = max(glm.dot(hit.normal, to_light), 0.0) * visibility
        return entity.material.color * (scene.light.ambient + diffuse * scene.light.color)

    def render(self, scene: Scene) -> None:
        width, height = self._size
        for y in range(height):
            for x in range(width):
                ray = scene.camera.ray_through((x + 0.5) / width, (y + 0.5) / height)
                self._set_pixel(x, y, self._trace(scene, ray))
        self._texture.write(bytes(self._pixels))
        self._screen.draw(self._texture)
