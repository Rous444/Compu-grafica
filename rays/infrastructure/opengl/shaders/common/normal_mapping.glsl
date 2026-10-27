#ifndef NORMAL_MAPPING_GLSL
#define NORMAL_MAPPING_GLSL

// Convierte un texel del normal map (espacio tangente, codificado en [0, 1]) en una normal del mundo.
vec3 perturb_normal(vec3 normal, vec3 tangent, vec3 encoded_normal) {
    tangent = normalize(tangent - normal * dot(normal, tangent));
    vec3 bitangent = cross(normal, tangent);
    vec3 tangent_space_normal = encoded_normal * 2.0 - 1.0;
    return normalize(mat3(tangent, bitangent, normal) * tangent_space_normal);
}

#endif