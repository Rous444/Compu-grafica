#ifndef SCENE_QUERY_GLSL
#define SCENE_QUERY_GLSL

#include "common/ray.glsl"
#include "common/scene_types.glsl"
#include "common/intersections.glsl"
#include "common/normal_mapping.glsl"

// El shader principal declara el arreglo objects[] y el uniform u_object_count antes de incluir este archivo.

uniform sampler2DArray u_textures;

struct Hit {
    float distance;
    int object_index;
    vec3 local_point;
    vec3 local_normal;
};

struct Surface {
    vec3 point;
    vec3 geometric_normal;   // la normal de la cara, para desplazar los rayos secundarios
    vec3 normal;             // la normal con el normal map aplicado, para la iluminación
    vec3 albedo;
    float shininess;
    float reflectivity;
};

// Lleva el rayo al espacio local del objeto (sin normalizar la dirección) y prueba su forma.
bool intersect_object(int index, Ray ray, out float distance, out vec3 local_point, out vec3 local_normal) {
    mat4 inverse_model = objects[index].inverse_model;
    vec3 origin = (inverse_model * vec4(ray.origin, 1.0)).xyz;
    vec3 direction = (inverse_model * vec4(ray.direction, 0.0)).xyz;
    bool found;
    if (int(objects[index].shape_layers.x) == SHAPE_BOX) {
        found = intersect_local_box(origin, direction, distance, local_normal);
    } else {
        found = intersect_local_rect(origin, direction, distance, local_normal);
    }
    local_point = origin + direction * distance;
    return found;
}

// El objeto más cercano que golpea el rayo. Igual que closest_hit en Python.
bool closest_hit(Ray ray, out Hit hit) {
    hit.distance = NO_HIT;
    hit.object_index = -1;
    for (int i = 0; i < u_object_count; i++) {
        float distance;
        vec3 local_point;
        vec3 local_normal;
        if (intersect_object(i, ray, distance, local_point, local_normal) && distance < hit.distance) {
            hit.distance = distance;
            hit.object_index = i;
            hit.local_point = local_point;
            hit.local_normal = local_normal;
        }
    }
    return hit.object_index >= 0;
}
// ¿Hay algún objeto en el camino? Para una sombra no importa cuál es el más cercano.
bool occluded(vec3 origin, vec3 direction) {
    Ray shadow_ray = Ray(origin, direction);
    for (int i = 0; i < u_object_count; i++) {
        float distance;
        vec3 local_point;
        vec3 local_normal;
        if (intersect_object(i, shadow_ray, distance, local_point, local_normal)) {
            return true;
        }
    }
    return false;
}


// Lo que necesitamos saber de la superficie en el punto de impacto.
Surface surface_at(Ray ray, Hit hit) {
    SceneObject object = objects[hit.object_index];
    Surface surface;
    surface.point = ray.origin + ray.direction * hit.distance;
    surface.geometric_normal = normalize(transpose(mat3(object.inverse_model)) * hit.local_normal);
    vec3 tangent = normalize(mat3(object.model) * face_tangent(hit.local_normal));
    vec2 uv = face_uv(hit.local_point, hit.local_normal) * object.shape_layers.w;
    // En el compute shader no hay derivadas de pantalla para elegir el mipmap: leemos el nivel 0.
    vec3 base_color = textureLod(u_textures, vec3(uv, object.shape_layers.y), 0.0).rgb;
    vec3 encoded_normal = textureLod(u_textures, vec3(uv, object.shape_layers.z), 0.0).rgb;
    surface.normal = perturb_normal(surface.geometric_normal, tangent, encoded_normal);
    surface.albedo = object.color_reflectivity.rgb * base_color;
    surface.shininess = object.material_extra.x;
    surface.reflectivity = object.color_reflectivity.a;
    return surface;
}

#endif