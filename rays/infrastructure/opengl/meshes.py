from dataclasses import dataclass

from pyglm import glm

from domain.shapes import Box, Rect, Shape

VERTEX_FORMAT = "3f"
VERTEX_ATTRIBUTES = ("in_position",)


@dataclass(frozen=True)
class MeshData:
    vertices: glm.array
    indices: glm.array


BOX_MESH = MeshData(
    vertices=glm.array(
        glm.float32,
        -1.0, -1.0, -1.0,
         1.0, -1.0, -1.0,
         1.0,  1.0, -1.0,
        -1.0,  1.0, -1.0,
        -1.0, -1.0,  1.0,
         1.0, -1.0,  1.0,
         1.0,  1.0,  1.0,
        -1.0,  1.0,  1.0,
    ),
    indices=glm.array(
        glm.uint32,
        0, 1, 2, 2, 3, 0,  # back
        4, 5, 6, 6, 7, 4,  # front
        0, 4, 7, 7, 3, 0,  # left
        1, 5, 6, 6, 2, 1,  # right
        3, 2, 6, 6, 7, 3,  # top
        0, 1, 5, 5, 4, 0,  # bottom
    ),
)

RECT_MESH = MeshData(
    vertices=glm.array(
        glm.float32,
        -1.0, 0.0, -1.0,
         1.0, 0.0, -1.0,
         1.0, 0.0,  1.0,
        -1.0, 0.0,  1.0,
    ),
    indices=glm.array(glm.uint32, 0, 1, 2, 2, 3, 0),
)

_MESHES: dict[type[Shape], MeshData] = {
    Box: BOX_MESH,
    Rect: RECT_MESH,
}


def mesh_for(shape: Shape) -> MeshData:
    mesh = _MESHES.get(type(shape))
    if mesh is None:
        raise TypeError(f"No mesh available for shape {type(shape).__name__}")
    return mesh
