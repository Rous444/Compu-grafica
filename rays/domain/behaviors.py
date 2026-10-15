import math
from dataclasses import dataclass, field
from typing import Protocol

from pyglm import glm

from domain.transform import Transform


class Behavior(Protocol):
    def update(self, transform: Transform, delta_seconds: float) -> None: ...


@dataclass
class Spin:
    degrees_per_second: glm.vec3

    def update(self, transform: Transform, delta_seconds: float) -> None:
        transform.rotation_degrees = (transform.rotation_degrees + self.degrees_per_second * delta_seconds) % 360.0


@dataclass
class Oscillate:
    axis: glm.vec3
    amplitude: float
    frequency_hz: float
    _elapsed: float = field(default=0.0, init=False)
    _offset: glm.vec3 = field(default_factory=lambda: glm.vec3(0.0), init=False)

    def update(self, transform: Transform, delta_seconds: float) -> None:
        self._elapsed += delta_seconds
        phase = 2.0 * math.pi * self.frequency_hz * self._elapsed
        new_offset = glm.normalize(self.axis) * self.amplitude * math.sin(phase)
        transform.position += new_offset - self._offset
        self._offset = new_offset
