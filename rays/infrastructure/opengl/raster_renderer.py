import moderngl

from domain.entity import Entity
from domain.scene import Scene
from domain.shapes import Shape
from infrastructure.opengl.meshes import VERTEX_ATTRIBUTES, VERTEX_FORMAT, mesh_for
from infrastructure.opengl.shader_loader import load_program

class RasterRenderer:
    def __init__(self, context: moderngl.Context) -> None:
        self._context = context
        self._program = load_program(context, "raster")
        self._vertex_arrays: dict[type[Shape], moderngl.VertexArray] = {}
        self._context.enable(moderngl.DEPTH_TEST)

    def resize(self, framebuffer_width: int, framebuffer_height: int) -> None:
        self._context.viewport = (0, 0, framebuffer_width, framebuffer_height)

    def render(self, scene: Scene) -> None:
        self._context.clear(*scene.background_color)
        camera = scene.camera
        self._program["u_view_projection"].write(camera.projection_matrix() * camera.view_matrix())
        for entity in scene.entities:
            self._draw(entity)

    def _draw(self, entity: Entity) -> None:
        self._program["u_model"].write(entity.transform.model_matrix())
        self._program["u_color"].write(entity.material.color)
        self._vertex_array_for(entity.shape).render()

    def _vertex_array_for(self, shape: Shape) -> moderngl.VertexArray:
        shape_type = type(shape)
        if shape_type not in self._vertex_arrays:
            mesh = mesh_for(shape)
            vertex_buffer = self._context.buffer(mesh.vertices)
            index_buffer = self._context.buffer(mesh.indices)
            self._vertex_arrays[shape_type] = self._context.vertex_array(
                self._program,
                [(vertex_buffer, VERTEX_FORMAT, *VERTEX_ATTRIBUTES)],
                index_buffer=index_buffer,
                index_element_size=4,
            )
        return self._vertex_arrays[shape_type]
