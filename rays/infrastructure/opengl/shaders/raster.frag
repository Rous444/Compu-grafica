#version 330 core

in vec3 v_world_position;
in vec2 v_uv;
in vec3 v_normal;
in vec3 v_tangent;

out vec4 frag_color;

uniform vec3 u_color;
uniform float u_shininess;
uniform vec3 u_camera_position;
uniform sampler2D u_base_color_map;
uniform sampler2D u_normal_map;
uniform vec3 u_to_light;
uniform vec3 u_light_color;
uniform float u_ambient;

const float SPECULAR_STRENGTH = 0.5;

// Convierte un texel del normal map (espacio tangente, codificado en [0, 1]) en una normal del mundo.
vec3 perturb_normal(vec3 normal, vec3 tangent, vec3 encoded_normal) {
    tangent = normalize(tangent - normal * dot(normal, tangent));
    vec3 bitangent = cross(normal, tangent);
    vec3 tangent_space_normal = encoded_normal * 2.0 - 1.0;
    return normalize(mat3(tangent, bitangent, normal) * tangent_space_normal);
}

void main() {
    vec3 albedo = u_color * texture(u_base_color_map, v_uv).rgb;
    vec3 encoded_normal = texture(u_normal_map, v_uv).rgb;
    vec3 normal = perturb_normal(normalize(v_normal), normalize(v_tangent), encoded_normal);
    vec3 view_direction = normalize(u_camera_position - v_world_position);

    float diffuse = max(dot(normal, u_to_light), 0.0);
    vec3 half_vector = normalize(u_to_light + view_direction);
    float specular = diffuse > 0.0 ? pow(max(dot(normal, half_vector), 0.0), u_shininess) : 0.0;

    vec3 color = albedo * u_ambient + (albedo * diffuse + vec3(specular * SPECULAR_STRENGTH)) * u_light_color;
    frag_color = vec4(color, 1.0);
}
