#ifndef SKY_GLSL
#define SKY_GLSL

uniform vec3 u_sky_top;
uniform vec3 u_sky_bottom;

// Mismo degradé que SkyGradient.color_for en Python.
vec3 sky_color(vec3 direction) {
    float blend = 0.5 * (direction.y + 1.0);
    return mix(u_sky_bottom, u_sky_top, blend);
}

#endif