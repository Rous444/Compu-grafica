#version 330 core

#include "common/lighting.glsl"
#include "common/normal_mapping.glsl"

in vec3 v_world_position;
in vec3 v_normal;
in vec3 v_tangent;
in vec2 v_uv;

out vec4 frag_color;

uniform vec3 u_color;
uniform sampler2D u_base_color_map;
uniform sampler2D u_normal_map;
uniform float u_shininess;
uniform vec3 u_camera_position;
uniform vec3 u_to_light;
uniform vec3 u_light_color;
uniform float u_ambient;

void main() {
    vec3 albedo = u_color * texture(u_base_color_map, v_uv).rgb;
    vec3 encoded_normal = texture(u_normal_map, v_uv).rgb;
    vec3 normal = perturb_normal(normalize(v_normal), normalize(v_tangent), encoded_normal);
    vec3 view_direction = normalize(u_camera_position - v_world_position);
    // El raster no sabe si hay otro objeto entre el punto y la luz: siempre la ve (visibilidad 1).
    vec3 color = blinn_phong(albedo, normal, view_direction, u_to_light, u_light_color, u_ambient, u_shininess, 1.0);
    frag_color = vec4(color, 1.0);
}