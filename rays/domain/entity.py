from dataclasses import dataclass, field

from domain.behaviors import Behavior
from domain.material import Material
from domain.shapes import Shape
from domain.transform import Transform


@dataclass
class Entity:
    name: str
    shape: Shape
    transform: Transform = field(default_factory=Transform)
    material: Material = field(default_factory=Material)
    behaviors: list[Behavior] = field(default_factory=list)

    def update(self, delta_seconds: float) -> None:
        for behavior in self.behaviors:
            behavior.update(self.transform, delta_seconds)
