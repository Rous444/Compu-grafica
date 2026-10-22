import moderngl
from pyglm import glm

from domain.entity import Entity
from domain.scene import Scene
from domain.shapes import Shape
from infrastructure.opengl.meshes import VERTEX_ATTRIBUTES, VERTEX_FORMAT, mesh_for
from infrastructure.opengl.shader_loader import load_program
from infrastructure.opengl.texture_library import TextureLibrary

BASE_COLOR_UNIT = 0
NORMAL_MAP_UNIT = 1


class RasterRenderer:
    def __init__(self, context: moderngl.Context, textures: TextureLibrary) -> None:
        self._context = context
        self._textures = textures
        self._program = load_program(context, "raster")
        self._vertex_arrays: dict[type[Shape], moderngl.VertexArray] = {}
        self._context.enable(moderngl.DEPTH_TEST)

    def resize(self, framebuffer_width: int, framebuffer_height: int) -> None:
        self._context.viewport = (0, 0, framebuffer_width, framebuffer_height)

    def render(self, scene: Scene) -> None:
        self._context.clear(*scene.background_color)
        camera = scene.camera
        self._program["u_camera_position"].write(camera.position)
        self._program["u_view_projection"].write(camera.projection_matrix() * camera.view_matrix())
        self._program["u_base_color_map"] = BASE_COLOR_UNIT
        self._program["u_normal_map"] = NORMAL_MAP_UNIT
        self._program["u_to_light"].write(scene.light.to_light())
        self._program["u_light_color"].write(scene.light.color)
        self._program["u_ambient"] = scene.light.ambient
        for entity in scene.entities:
            self._draw(entity)

    def _draw(self, entity: Entity) -> None:
        material = entity.material
        model = entity.transform.model_matrix()
        self._program["u_model"].write(model)
        self._program["u_normal_matrix"].write(glm.transpose(glm.inverse(glm.mat3(model))))
        self._program["u_color"].write(material.color)
        self._program["u_uv_scale"] = material.uv_scale
        self._program["u_shininess"] = material.shininess
        self._textures.texture(material.base_color_map, "base").use(location=BASE_COLOR_UNIT)
        self._textures.texture(material.normal_map, "normal").use(location=NORMAL_MAP_UNIT)
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
