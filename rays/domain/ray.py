from dataclasses import dataclass

from pyglm import glm


@dataclass(frozen=True)
class Ray:
    """Semirrecta definida por un origen y una dirección. La dirección siempre se guarda normalizada."""

    origin: glm.vec3
    direction: glm.vec3

    def __post_init__(self) -> None:
        object.__setattr__(self, "origin", glm.vec3(self.origin))
        object.__setattr__(self, "direction", glm.normalize(glm.vec3(self.direction)))

    def point_at(self, distance: float) -> glm.vec3:
        """Punto del rayo a cierta distancia del origen: P(t) = origen + t * dirección."""
        return self.origin + self.direction * distance