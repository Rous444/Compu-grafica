#ifndef RAYTRACING_GLSL
#define RAYTRACING_GLSL

#include "common/scene_query.glsl"
#include "common/sky.glsl"

#include "common/lighting.glsl"

uniform vec3 u_to_light;
uniform vec3 u_light_color;
uniform float u_ambient;
uniform int u_max_bounces;

const float SURFACE_OFFSET = 1e-3;

// Luz que el punto de la superficie refleja hacia quien lo mira (dirección view_direction).
vec3 shade(Surface surface, vec3 view_direction) {
    vec3 offset_point = surface.point + surface.geometric_normal * SURFACE_OFFSET;
    float visibility = occluded(offset_point, u_to_light) ? 0.0 : 1.0;
    return blinn_phong(surface.albedo, surface.normal, view_direction, u_to_light,
                       u_light_color, u_ambient, surface.shininess, visibility);
}

// Color que ve un rayo: el color de la superficie más cercana, o el cielo.
// Color que ve un rayo, siguiendo sus reflejos (raytracing de Whitted).
// throughput: cuánto de lo que ve el rayo actual llega a la cámara (se achica en cada rebote).
vec3 trace(Ray ray) {
    vec3 color = vec3(0.0);
    vec3 throughput = vec3(1.0);
    for (int bounce = 0; bounce <= u_max_bounces; bounce++) {
        Hit hit;
        if (!closest_hit(ray, hit)) {
            color += throughput * sky_color(ray.direction);
            break;
        }
        Surface surface = surface_at(ray, hit);
        color += throughput * (1.0 - surface.reflectivity) * shade(surface, -ray.direction);
        if (surface.reflectivity <= 0.0) {
            break;
        }
                throughput *= surface.reflectivity;
        vec3 offset_point = surface.point + surface.geometric_normal * SURFACE_OFFSET;
        ray = Ray(offset_point, reflect(ray.direction, surface.normal));
        }
        return color;
}

#endif