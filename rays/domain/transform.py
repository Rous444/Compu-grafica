from dataclasses import dataclass, field

from pyglm import glm


@dataclass
class Transform:
    position: glm.vec3 = field(default_factory=lambda: glm.vec3(0.0))
    rotation_degrees: glm.vec3 = field(default_factory=lambda: glm.vec3(0.0))
    scale: glm.vec3 = field(default_factory=lambda: glm.vec3(1.0))

    def model_matrix(self) -> glm.mat4:
        matrix = glm.translate(glm.mat4(1.0), self.position)
        matrix = glm.rotate(matrix, glm.radians(self.rotation_degrees.x), glm.vec3(1, 0, 0))
        matrix = glm.rotate(matrix, glm.radians(self.rotation_degrees.y), glm.vec3(0, 1, 0))
        matrix = glm.rotate(matrix, glm.radians(self.rotation_degrees.z), glm.vec3(0, 0, 1))
        return glm.scale(matrix, self.scale)
