#version 330 core

in vec2 v_uv;

out vec4 frag_color;

uniform sampler2D u_image;

void main() {
    frag_color = vec4(texture(u_image, v_uv).rgb, 1.0);
}