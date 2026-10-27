#ifndef INTERSECTIONS_GLSL
#define INTERSECTIONS_GLSL

const float EPSILON = 1e-4;
const float NO_HIT = 1e30;

// Método de slabs en espacio local, donde la caja va de -1 a 1. Igual que _slab en Python.
bool intersect_local_box(vec3 origin, vec3 direction, out float distance, out vec3 normal) {
    vec3 inverse_direction = 1.0 / direction;   // en GLSL, 1.0 / 0.0 da infinito sin error
    vec3 t_min = (vec3(-1.0) - origin) * inverse_direction;
    vec3 t_max = (vec3(1.0) - origin) * inverse_direction;
    vec3 t1 = min(t_min, t_max);
    vec3 t2 = max(t_min, t_max);
    float t_near = max(max(t1.x, t1.y), t1.z);
    float t_far = min(min(t2.x, t2.y), t2.z);
    if (t_near > t_far || t_near < EPSILON) {
        return false;
    }
    distance = t_near;
    // step(a, b) vale 1 si b >= a: el eje cuyo t1 es igual a t_near queda en 1, los otros en 0.
    vec3 entry_axis = step(vec3(t_near), t1) * step(t1, vec3(t_near));
    normal = -sign(direction) * entry_axis;
    return true;
}

// Rayo contra el plano local y = 0, recortado al cuadrado |x| <= 1, |z| <= 1. Igual que intersect_rect.
bool intersect_local_rect(vec3 origin, vec3 direction, out float distance, out vec3 normal) {
    if (abs(direction.y) < 1e-9) {
        return false;
    }
    distance = -origin.y / direction.y;
    vec3 point = origin + direction * distance;
    normal = vec3(0.0, 1.0, 0.0);
    return distance > EPSILON && abs(point.x) <= 1.0 && abs(point.z) <= 1.0;
}

// Tangente de cada cara (hacia dónde crece u). Es la misma tabla que BOX_FACES en meshes.py.
vec3 face_tangent(vec3 local_normal) {
    if (local_normal.x > 0.5) return vec3(0.0, 0.0, -1.0);
    if (local_normal.x < -0.5) return vec3(0.0, 0.0, 1.0);
    if (abs(local_normal.y) > 0.5) return vec3(1.0, 0.0, 0.0);
    if (local_normal.z > 0.5) return vec3(1.0, 0.0, 0.0);
    return vec3(-1.0, 0.0, 0.0);
}

// UV del punto de impacto: la misma cuenta que usa meshes.py para los vértices.
vec2 face_uv(vec3 local_point, vec3 local_normal) {
    vec3 tangent = face_tangent(local_normal);
    vec3 bitangent = cross(local_normal, tangent);
    return vec2(dot(local_point, tangent), dot(local_point, bitangent)) * 0.5 + 0.5;
}

#endif