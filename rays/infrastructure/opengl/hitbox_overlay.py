import moderngl
from pyglm import glm

from domain.entity import Entity
from domain.scene import Scene
from domain.shapes import Box, Rect, Shape
from infrastructure.opengl.shader_loader import load_program

HITBOX_COLOR = glm.vec3(0.2, 1.0, 0.3)
BOX_CORNERS = [glm.vec3(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
RECT_CORNERS = [glm.vec3(-1, 0, -1), glm.vec3(1, 0, -1), glm.vec3(1, 0, 1), glm.vec3(-1, 0, 1)]


def _box_edges() -> list[glm.vec3]:
    """Las 12 aristas del cubo local: pares de esquinas que difieren en una sola coordenada."""
    edges = []
    for i, start in enumerate(BOX_CORNERS):
        for end in BOX_CORNERS[i + 1:]:
            if sum(start[axis] != end[axis] for axis in range(3)) == 1:
                edges.extend((start, end))
    return edges


def _rect_edges() -> list[glm.vec3]:
    """Los 4 lados del cuadrado local del piso."""
    edges = []
    for i, start in enumerate(RECT_CORNERS):
        edges.extend((start, RECT_CORNERS[(i + 1) % len(RECT_CORNERS)]))
    return edges


EDGES: dict[type[Shape], list[glm.vec3]] = {Box: _box_edges(), Rect: _rect_edges()}


class HitboxOverlay:
    """Dibuja con líneas, por encima de la escena, el hitbox de las entidades que lo tienen activado."""

    def __init__(self, context: moderngl.Context) -> None:
        self._context = context
        self._program = load_program(context, "hitbox")
        self._vertex_arrays = {
            shape_type: context.vertex_array(
                self._program, [(context.buffer(glm.array(edges)), "3f", "in_position")])
            for shape_type, edges in EDGES.items()
        }

    def resize(self, framebuffer_width: int, framebuffer_height: int) -> None:
        """El overlay dibuja sobre el mismo viewport que el renderer, así que no necesita hacer nada."""

    def render(self, scene: Scene) -> None:
        visible = [entity for entity in scene.entities if entity.show_hitbox]
        if not visible:
            return
        # Sin depth test: el hitbox se ve aunque quede detrás de la superficie, como en los editores.
        self._context.disable(moderngl.DEPTH_TEST)
        camera = scene.camera
        self._program["u_view_projection"].write(camera.projection_matrix() * camera.view_matrix())
        self._program["u_color"].write(HITBOX_COLOR)
        for entity in visible:
            self._program["u_model"].write(self._hitbox_matrix(entity))
            self._vertex_arrays[type(entity.shape)].render(mode=moderngl.LINES)
        self._context.enable(moderngl.DEPTH_TEST)

    @staticmethod
    def _hitbox_matrix(entity: Entity) -> glm.mat4:
        """Matriz que lleva la forma local (de -1 a 1) hasta el hitbox OBB de la entidad."""
        return entity.transform.model_matrix()