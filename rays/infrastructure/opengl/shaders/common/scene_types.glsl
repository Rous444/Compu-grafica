#ifndef SCENE_TYPES_GLSL
#define SCENE_TYPES_GLSL

const int SHAPE_BOX = 0;
const int SHAPE_RECT = 1;

// Un objeto de la escena tal como lo arma GpuScene en Python.
// Solo usa mat4 y vec4: así ocupa lo mismo en un SSBO (std430) y en un UBO (std140).
struct SceneObject {
    mat4 model;
    mat4 inverse_model;
    vec4 color_reflectivity;   // rgb: color del material, a: reflectividad
    vec4 shape_layers;         // x: forma, y: capa del color base, z: capa del normal map, w: uv_scale
    vec4 material_extra;       // x: shininess (y, z, w sin usar: completan los 16 bytes)
};

#endif