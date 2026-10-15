from dataclasses import dataclass, field

from pyglm import glm


@dataclass
class Material:
    color: glm.vec3 = field(default_factory=lambda: glm.vec3(0.8))

    @classmethod
    def from_rgb255(cls, red: int, green: int, blue: int) -> "Material":
        return cls(color=glm.vec3(red, green, blue) / 255.0)
