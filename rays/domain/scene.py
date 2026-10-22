from dataclasses import dataclass, field

from pyglm import glm

from domain.camera import Camera
from domain.entity import Entity
from domain.lighting import DirectionalLight, SkyGradient
from domain.intersections import Hit, closest_hit
from domain.ray import Ray


@dataclass
class Scene:
    camera: Camera
    background_color: glm.vec3 = field(default_factory=lambda: glm.vec3(0.2, 0.2, 0.2))
    entities: list[Entity] = field(default_factory=list)
    light: DirectionalLight = field(default_factory=DirectionalLight)
    sky: SkyGradient = field(default_factory=SkyGradient)

    def add(self, entity: Entity) -> Entity:
        if any(existing.name == entity.name for existing in self.entities):
            raise ValueError(f"An entity named '{entity.name}' already exists")
        self.entities.append(entity)
        return entity

    def update(self, delta_seconds: float) -> None:
        for entity in self.entities:
            entity.update(delta_seconds)
    def pick(self, ray: Ray) -> tuple[Entity, Hit] | None:
        return closest_hit(ray, self.entities)
