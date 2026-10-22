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


@dataclass
class SkyGradient:
    """Cielo de fondo: un degradé entre un color en el horizonte y otro arriba."""

    top: glm.vec3 = field(default_factory=lambda: glm.vec3(16, 150, 222) / 255.0)
    bottom: glm.vec3 = field(default_factory=lambda: glm.vec3(181, 224, 247) / 255.0)

    def color_for(self, direction: glm.vec3) -> glm.vec3:
        """Color del cielo en la dirección de un rayo que no chocó con nada."""
        # direction.y va de -1 (abajo) a 1 (arriba); lo llevamos a [0, 1] para mezclar.
        blend = 0.5 * (direction.y + 1.0)
        return glm.mix(self.bottom, self.top, blend)
