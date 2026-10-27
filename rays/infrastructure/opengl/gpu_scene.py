import struct

import moderngl
from pyglm import glm

from domain.entity import Entity
from domain.scene import Scene
from domain.shapes import Box
from infrastructure.opengl.texture_library import FLAT_NORMAL_LAYER, WHITE_LAYER, TextureLibrary

MAX_OBJECTS = 32
SHAPE_BOX, SHAPE_RECT = 0, 1
OBJECT_SIZE = 176  # bytes: mat4 + mat4 + 3 vec4 = 64 + 64 + 48
TEXTURE_ARRAY_UNIT = 1
MAX_BOUNCES = 2

ShaderProgram = moderngl.Program | moderngl.ComputeShader

class GpuScene:
    """Traduce la escena del dominio a los datos que necesitan los shaders de raytracing."""

    def __init__(self, context: moderngl.Context, textures: TextureLibrary, scene: Scene) -> None:
        paths = [path for entity in scene.entities
                 for path in (entity.material.base_color_map, entity.material.normal_map) if path]
        self._texture_array, self._layer_of = textures.texture_array(paths)
        self.objects_buffer = context.buffer(reserve=OBJECT_SIZE * MAX_OBJECTS)
        self._object_count = 0

    def apply(self, program: ShaderProgram, scene: Scene, aspect_ratio: float) -> None:
        camera = scene.camera
        self._texture_array.use(location=TEXTURE_ARRAY_UNIT)
        self._set_uniforms(program, {
            "u_object_count": self._object_count,
            "u_textures": TEXTURE_ARRAY_UNIT,
            "u_inverse_view": glm.inverse(camera.view_matrix()),
            "u_camera_position": camera.position,
            "u_tan_half_fov": camera.tan_half_fov(),
            "u_aspect_ratio": aspect_ratio,
            "u_sky_top": scene.sky.top,
            "u_sky_bottom": scene.sky.bottom,
            "u_to_light": scene.light.to_light(),
            "u_light_color": scene.light.color,
            "u_ambient": scene.light.ambient,
            "u_max_bounces": MAX_BOUNCES,
        })
        
    @staticmethod
    def _set_uniforms(program: ShaderProgram, values: dict) -> None:
        """Asigna cada uniform. Si el shader no lo usa (el compilador lo eliminó), lo saltea."""
        for name, value in values.items():
            uniform = program.get(name, None)
            if uniform is None:
                continue
            if isinstance(value, (int, float)):
                uniform.value = value
            else:
                uniform.write(value)

    def upload(self, scene: Scene) -> None:
        """Escribe en el buffer los datos actuales de cada entidad (se mueven en cada frame)."""
        entities = scene.entities[:MAX_OBJECTS]
        self.objects_buffer.write(b"".join(self._pack(entity) for entity in entities))
        self._object_count = len(entities)

    def _pack(self, entity: Entity) -> bytes:
        """Los bytes de un SceneObject, en el mismo orden que el struct de scene_types.glsl."""
        material = entity.material
        model = entity.transform.model_matrix()
        shape = SHAPE_BOX if isinstance(entity.shape, Box) else SHAPE_RECT
        base_layer = self._layer_of.get(material.base_color_map, WHITE_LAYER)
        normal_layer = self._layer_of.get(material.normal_map, FLAT_NORMAL_LAYER)
        return b"".join((
            model.to_bytes(),
            glm.inverse(model).to_bytes(),
            struct.pack("4f", *material.color, material.reflectivity),
            struct.pack("4f", shape, base_layer, normal_layer, material.uv_scale),
            struct.pack("4f", material.shininess, 0.0, 0.0, 0.0),
        ))