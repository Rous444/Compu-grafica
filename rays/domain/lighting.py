from dataclasses import dataclass, field

from pyglm import glm


@dataclass
class DirectionalLight:
    """Una luz que viene de una dirección constante, como el sol. La luz viaja a través de esa dirección."""

    direction: glm.vec3 = field(default_factory=lambda: glm.vec3(-0.5, -1.0, -0.4))
    color: glm.vec3 = field(default_factory=lambda: glm.vec3(1.0, 0.97, 0.9))
    ambient: float = 0.15

    def to_light(self) -> glm.vec3:
        return -glm.normalize(self.direction)