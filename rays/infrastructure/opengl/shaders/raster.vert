#version 330 core

in vec3 in_position;
in vec2 in_uv;
in vec3 in_normal;
in vec3 in_tangent;

uniform mat4 u_model;
uniform mat4 u_view_projection;
uniform mat3 u_normal_matrix;
uniform float u_uv_scale;

out vec3 v_world_position;
out vec3 v_normal;
out vec2 v_uv;
out vec3 v_tangent;

void main() {
    vec4 world_position = u_model * vec4(in_position, 1.0);
    v_world_position = world_position.xyz;
    v_normal = u_normal_matrix * in_normal;
    v_tangent = mat3(u_model) * in_tangent;
    v_uv = in_uv * u_uv_scale;
    gl_Position = u_view_projection * world_position;
}
