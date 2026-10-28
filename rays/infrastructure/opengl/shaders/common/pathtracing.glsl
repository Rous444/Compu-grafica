#ifndef PATHTRACING_GLSL
#define PATHTRACING_GLSL

#include "common/scene_query.glsl"
#include "common/sky.glsl"

uniform vec3 u_to_light;
uniform vec3 u_light_color;
uniform int u_max_bounces;

const float SURFACE_OFFSET = 1e-3;
const float PI = 3.14159265359;
const float SKY_INTENSITY = 0.6;          // cuánta luz aporta el cielo a lo que ilumina
const float SUN_ANGULAR_RADIUS = 0.04;    // radianes: un sol con tamaño da sombras suaves

// Hash PCG: GLSL no tiene random(), así que lo armamos con operaciones de enteros.
uint pcg_hash(uint value) {
    uint state = value * 747796405u + 2891336453u;
    uint word = ((state >> ((state >> 28u) + 4u)) ^ state) * 277803737u;
    return (word >> 22u) ^ word;
}

// Cada píxel y cada frame arrancan con una semilla distinta, para que el ruido no forme patrones.
uint seed_for(ivec2 pixel, int frame_index) {
    return pcg_hash(uint(pixel.x) + pcg_hash(uint(pixel.y) + pcg_hash(uint(frame_index))));
}

// Número al azar entre 0 y 1. Cada llamada avanza el estado.
float random01(inout uint state) {
    state = pcg_hash(state);
    return float(state) / 4294967295.0;
}

// Base ortonormal alrededor de una dirección, para armar direcciones relativas a ella.
mat3 basis_around(vec3 direction) {
    vec3 helper = abs(direction.x) > 0.9 ? vec3(0.0, 1.0, 0.0) : vec3(1.0, 0.0, 0.0);
    vec3 tangent = normalize(cross(helper, direction));
    return mat3(tangent, cross(direction, tangent), direction);
}

// Dirección al azar en el hemisferio de la normal, con más probabilidad cerca de la normal
// (distribución coseno). Es el rebote de una superficie mate ideal.
vec3 cosine_hemisphere(vec3 normal, inout uint state) {
    float angle = 2.0 * PI * random01(state);
    float radius_squared = random01(state);
    float radius = sqrt(radius_squared);
    vec3 local = vec3(cos(angle) * radius, sin(angle) * radius, sqrt(1.0 - radius_squared));
    return normalize(basis_around(normal) * local);
}

// Dirección al azar hacia algún punto del disco del sol.
vec3 sample_sun(inout uint state) {
    float angle = 2.0 * PI * random01(state);
    float radius = SUN_ANGULAR_RADIUS * sqrt(random01(state));
    return normalize(basis_around(u_to_light) * vec3(cos(angle) * radius, sin(angle) * radius, 1.0));
}

// Un camino de luz: el rayo rebota al azar hasta salir al cielo o agotar los rebotes.
vec3 trace_path(Ray ray, inout uint state) {
    vec3 radiance = vec3(0.0);
    vec3 throughput = vec3(1.0);
    for (int bounce = 0; bounce < u_max_bounces; bounce++) {
        Hit hit;
        if (!closest_hit(ray, hit)) {
            // El cielo visto directamente se ve con su color; como luz que rebota, ilumina menos.
            float intensity = bounce == 0 ? 1.0 : SKY_INTENSITY;
            radiance += throughput * sky_color(ray.direction) * intensity;
            break;
        }
        Surface surface = surface_at(ray, hit);
        vec3 offset_point = surface.point + surface.geometric_normal * SURFACE_OFFSET;

        // Estimación directa de la luz: el sol es muy chico y un rebote al azar casi nunca lo
        // encontraría, así que en cada rebote le mandamos un rayo de sombra.
        vec3 to_sun = sample_sun(state);
        float sun = max(dot(surface.normal, to_sun), 0.0);
        if (sun > 0.0 && !occluded(offset_point, to_sun)) {
            radiance += throughput * surface.albedo * u_light_color * sun * (1.0 - surface.reflectivity);
        }

        // Rebote: espejo con probabilidad igual a la reflectividad; si no, difuso al azar.
        if (random01(state) < surface.reflectivity) {
            ray = Ray(offset_point, reflect(ray.direction, surface.normal));
        } else {
            ray = Ray(offset_point, cosine_hemisphere(surface.normal, state));
            throughput *= surface.albedo;
        }
    }
    return radiance;
}

// Varios caminos por píxel en cada frame, con un desplazamiento al azar dentro del píxel (antialiasing).
vec3 sample_pixel(ivec2 pixel, vec2 resolution, int samples, inout uint state) {
    vec3 total = vec3(0.0);
    for (int i = 0; i < samples; i++) {
        vec2 jitter = vec2(random01(state), random01(state));
        total += trace_path(camera_ray((vec2(pixel) + jitter) / resolution), state);
    }
    return total / float(samples);
}

#endif
