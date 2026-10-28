#version 330 core

// Alternativa para macOS: la acumulación usa dos texturas que se turnan (ping-pong).

#include "common/scene_types.glsl"

const int MAX_OBJECTS = 32;
layout(std140) uniform SceneObjects {
    SceneObject objects[MAX_OBJECTS];
};
uniform int u_object_count;
uniform int u_frame_index;
uniform int u_samples_per_frame;
uniform sampler2D u_previous;
uniform vec2 u_resolution;

#include "common/pathtracing.glsl"

in vec2 v_uv;

out vec4 frag_color;

void main() {
    ivec2 pixel = ivec2(gl_FragCoord.xy);
    uint state = seed_for(pixel, u_frame_index);
    vec3 frame_color = sample_pixel(pixel, u_resolution, u_samples_per_frame, state);
    vec3 previous = texture(u_previous, v_uv).rgb;
    frag_color = vec4(mix(previous, frame_color, 1.0 / float(u_frame_index + 1)), 1.0);
}