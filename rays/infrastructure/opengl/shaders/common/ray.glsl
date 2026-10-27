#ifndef RAY_GLSL
#define RAY_GLSL

struct Ray {
    vec3 origin;
    vec3 direction;
};

uniform mat4 u_inverse_view;
uniform vec3 u_camera_position;
uniform float u_tan_half_fov;
uniform float u_aspect_ratio;

// screen_uv va de 0 a 1, con (0, 0) abajo a la izquierda. Es la misma cuenta que Camera.ray_through.
Ray camera_ray(vec2 screen_uv) {
    vec2 ndc = screen_uv * 2.0 - 1.0;
    vec3 direction_camera = vec3(ndc.x * u_tan_half_fov * u_aspect_ratio, ndc.y * u_tan_half_fov, -1.0);
    vec3 direction_world = normalize((u_inverse_view * vec4(direction_camera, 0.0)).xyz);
    return Ray(u_camera_position, direction_world);
}

#endif