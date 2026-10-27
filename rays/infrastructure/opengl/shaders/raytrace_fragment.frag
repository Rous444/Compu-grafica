#version 330 core

// Alternativa para OpenGL 3.3 / 4.1 (macOS): el mismo trazado, ejecutado una vez por fragmento
// de un rectángulo que cubre toda la pantalla.

#include "common/scene_types.glsl"

// Los objetos de la escena, en un UBO: un bloque de uniforms de tamaño fijo (OpenGL 3.3 no tiene SSBO).
const int MAX_OBJECTS = 32;
layout(std140) uniform SceneObjects {
    SceneObject objects[MAX_OBJECTS];
};
uniform int u_object_count;

#include "common/raytracing.glsl"

in vec2 v_uv;

out vec4 frag_color;

void main() {
    frag_color = vec4(clamp(trace(camera_ray(v_uv)), 0.0, 1.0), 1.0);
}