from pyglm import glm

from domain.behaviors import Oscillate, Spin
from domain.camera import Camera
from domain.entity import Entity
from domain.material import Material
from domain.scene import Scene
from domain.shapes import Box, Rect
from domain.transform import Transform


def build_scene(aspect_ratio: float) -> Scene:
    camera = Camera(position=glm.vec3(0, 3, 12), target=glm.vec3(0, 0, 0), aspect_ratio=aspect_ratio)
    scene = Scene(camera=camera)

    scene.add(Entity(
        name="RedCube",
        shape=Box(),
        transform=Transform(position=glm.vec3(-2, 0, 0), rotation_degrees=glm.vec3(0, 30, 0)),
        material=Material.from_rgb255(200, 40, 60),
        behaviors=[Spin(degrees_per_second=glm.vec3(0, 45, 0))],
    ))
    scene.add(Entity(
        name="BlueCube",
        shape=Box(),
        transform=Transform(position=glm.vec3(2, 0, 0), scale=glm.vec3(1.0, 0.5, 1.0)),
        material=Material.from_rgb255(40, 90, 220),
        behaviors=[Oscillate(axis=glm.vec3(0, 1, 0), amplitude=1.0, frequency_hz=0.25)],
    ))
    scene.add(Entity(
        name="Floor",
        shape=Rect(),
        transform=Transform(position=glm.vec3(0, -2, 0), scale=glm.vec3(8, 1, 8)),
        material=Material.from_rgb255(120, 120, 120),
    ))
    return scene
