from dataclasses import dataclass, field

from pyglm import glm


@dataclass
class Camera:
    position: glm.vec3
    target: glm.vec3
    up: glm.vec3 = field(default_factory=lambda: glm.vec3(0.0, 1.0, 0.0))
    vertical_fov_degrees: float = 45.0
    aspect_ratio: float = 16.0 / 9.0
    near: float = 0.1
    far: float = 100.0

    def view_matrix(self) -> glm.mat4:
        return glm.lookAt(self.position, self.target, self.up)

    def projection_matrix(self) -> glm.mat4:
        return glm.perspective(glm.radians(self.vertical_fov_degrees), self.aspect_ratio, self.near, self.far)

    def resize(self, width: int, height: int) -> None:
        if height > 0:
            self.aspect_ratio = width / height
