from dataclasses import dataclass, field

from pyglm import glm


@dataclass
class Material:
    color: glm.vec3 = field(default_factory=lambda: glm.vec3(0.8))
    base_color_map: str | None = None
    normal_map: str | None = None
    uv_scale: float = 1.0
    shininess: float = 32.0
    reflectivity: float = 0.0

    @classmethod
    def from_rgb255(cls, red: int, green: int, blue: int, **properties) -> "Material":
        return cls(color=glm.vec3(red, green, blue) / 255.0, **properties)