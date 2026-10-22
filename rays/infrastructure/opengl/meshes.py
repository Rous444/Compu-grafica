from dataclasses import dataclass

from pyglm import glm

from domain.shapes import Box, Rect, Shape

VERTEX_FORMAT = "3f 3f 2f 3f"
VERTEX_ATTRIBUTES = ("in_position", "in_normal", "in_uv", "in_tangent")

# Cada cara se describe con su normal (hacia dónde mira) y su tangente (hacia dónde crece u).
# La bitangente, hacia donde crece v, es cross(normal, tangente).
BOX_FACES = (
    (glm.vec3(1, 0, 0), glm.vec3(0, 0, -1)),   # derecha
    (glm.vec3(-1, 0, 0), glm.vec3(0, 0, 1)),   # izquierda
    (glm.vec3(0, 1, 0), glm.vec3(1, 0, 0)),    # arriba
    (glm.vec3(0, -1, 0), glm.vec3(1, 0, 0)),   # abajo
    (glm.vec3(0, 0, 1), glm.vec3(1, 0, 0)),    # adelante
    (glm.vec3(0, 0, -1), glm.vec3(-1, 0, 0)),  # atrás
)
RECT_FACES = ((glm.vec3(0, 1, 0), glm.vec3(1, 0, 0)),)
FACE_CORNERS = ((-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0))


@dataclass(frozen=True)
class MeshData:
    vertices: glm.array
    indices: glm.array


def _build_faces(faces: tuple[tuple[glm.vec3, glm.vec3], ...], face_offset: float) -> MeshData:
    """Cada cara tiene sus propios 4 vértices: una esquina compartida por 3 caras necesita una normal y una uv distintas en cada una."""
    vertex_values: list[float] = []
    index_values: list[int] = []
    for face_index, (normal, tangent) in enumerate(faces):
        bitangent = glm.cross(normal, tangent)
        for s, t in FACE_CORNERS:
            position = normal * face_offset + tangent * s + bitangent * t
            uv = glm.vec2(s, t) * 0.5 + 0.5
            vertex_values.extend((*position, *normal, *uv, *tangent))
        first = face_index * 4
        index_values.extend((first, first + 1, first + 2, first + 2, first + 3, first))
    return MeshData(
        vertices=glm.array(glm.float32, *vertex_values),
        indices=glm.array(glm.uint32, *index_values),
    )


BOX_MESH = _build_faces(BOX_FACES, face_offset=1.0)
RECT_MESH = _build_faces(RECT_FACES, face_offset=0.0)

_MESHES: dict[type[Shape], MeshData] = {
    Box: BOX_MESH,
    Rect: RECT_MESH,
}


def mesh_for(shape: Shape) -> MeshData:
    mesh = _MESHES.get(type(shape))
    if mesh is None:
        raise TypeError(f"No mesh available for shape {type(shape).__name__}")
    return mesh