from dataclasses import dataclass

from pyglm import glm

from domain.entity import Entity
from domain.ray import Ray
from domain.shapes import Box, Rect


EPSILON = 1e-4
LOCAL_BOX_MIN = glm.vec3(-1.0)
LOCAL_BOX_MAX = glm.vec3(1.0)

@dataclass(frozen=True)
class Hit:
    """Resultado de una intersección: a qué distancia y en qué punto del mundo chocó el rayo."""

    distance: float
    point: glm.vec3


def _safe_inverse(direction: glm.vec3) -> glm.vec3:
    """1 / dirección, componente a componente. Si una componente es 0, usa un número muy grande."""
    return glm.vec3(*(1.0 / c if abs(c) > 1e-12 else 1e12 for c in direction))


def _slab(origin: glm.vec3, direction: glm.vec3, box_min: glm.vec3, box_max: glm.vec3) -> float | None:
    """Método de slabs: distancia a la que el rayo entra en la caja, o None si no la toca."""
    inverse_direction = _safe_inverse(direction)
    t_min = (box_min - origin) * inverse_direction
    t_max = (box_max - origin) * inverse_direction
    t1 = glm.min(t_min, t_max)
    t2 = glm.max(t_min, t_max)
    t_near = max(t1.x, t1.y, t1.z)
    t_far = min(t2.x, t2.y, t2.z)
    if t_near > t_far or t_near < EPSILON:
        return None
    return t_near


def closest_hit(ray: Ray, entities: list[Entity]) -> tuple[Entity, Hit] | None:
    """La entidad más cercana que golpea el rayo, junto con su intersección."""
    closest: tuple[Entity, Hit] | None = None
    for entity in entities:
        hit = intersect(ray, entity)
        if hit is not None and (closest is None or hit.distance < closest[1].distance):
            closest = (entity, hit)
    return closest

def _local_ray(ray: Ray, entity: Entity) -> tuple[glm.vec3, glm.vec3]:
    """Lleva el rayo al espacio local de la entidad con la inversa de su matriz de modelo.

    La dirección local NO se normaliza: así, la distancia t vale lo mismo en el espacio local
    y en el mundo, y se puede comparar entre objetos.
    """
    inverse_model = glm.inverse(entity.transform.model_matrix())
    local_origin = glm.vec3(inverse_model * glm.vec4(ray.origin, 1.0))
    local_direction = glm.vec3(inverse_model * glm.vec4(ray.direction, 0.0))
    return local_origin, local_direction

def intersect_obb(ray: Ray, entity: Entity) -> Hit | None:
    """Caja orientada: en el espacio local, el cubo es una caja alineada de -1 a 1."""
    local_origin, local_direction = _local_ray(ray, entity)
    distance = _slab(local_origin, local_direction, LOCAL_BOX_MIN, LOCAL_BOX_MAX)
    if distance is None:
        return None
    return Hit(distance, ray.point_at(distance))

def intersect_rect(ray: Ray, entity: Entity) -> Hit | None:
    """Rayo contra el plano local y = 0, recortado al cuadrado |x| <= 1, |z| <= 1."""
    local_origin, local_direction = _local_ray(ray, entity)
    if abs(local_direction.y) < 1e-9:
        return None  # El rayo es paralelo al plano.
    distance = -local_origin.y / local_direction.y
    if distance < EPSILON:
        return None  # El plano está detrás del origen del rayo.
    local_point = local_origin + local_direction * distance
    if abs(local_point.x) > 1.0 or abs(local_point.z) > 1.0:
        return None  # Toca el plano, pero fuera del cuadrado.
    return Hit(distance, ray.point_at(distance))

def intersect(ray: Ray, entity: Entity) -> Hit | None:
    """Elige la intersección que corresponde a la forma de la entidad."""
    if isinstance(entity.shape, Box):
        return intersect_obb(ray, entity)
    if isinstance(entity.shape, Rect):
        return intersect_rect(ray, entity)
    raise TypeError(f"No intersection available for shape {type(entity.shape).__name__}")