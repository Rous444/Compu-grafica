#ifndef LIGHTING_GLSL
#define LIGHTING_GLSL

const float SPECULAR_STRENGTH = 0.5;

// Blinn-Phong: ambiente + difusa (Lambert) + especular (vector medio).
// visibility: 1.0 si el punto ve la luz, 0.0 si está en sombra.
vec3 blinn_phong(vec3 albedo, vec3 normal, vec3 view_direction, vec3 to_light,
                 vec3 light_color, float ambient, float shininess, float visibility) {
    float diffuse = max(dot(normal, to_light), 0.0);
    vec3 half_vector = normalize(to_light + view_direction);
    float specular = diffuse > 0.0 ? pow(max(dot(normal, half_vector), 0.0), shininess) : 0.0;
    vec3 direct = (albedo * diffuse + vec3(specular * SPECULAR_STRENGTH)) * light_color * visibility;
    return albedo * ambient + direct;
}

#endif