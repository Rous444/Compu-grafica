#version 330 core

// Quad que cubre toda la pantalla, sin buffers: las 4 esquinas salen de gl_VertexID.
// Con TRIANGLE_STRIP, los vértices 0, 1, 2, 3 son (0, 0), (1, 0), (0, 1), (1, 1).
out vec2 v_uv;

void main() {
    vec2 corner = vec2(gl_VertexID & 1, (gl_VertexID >> 1) & 1);
    v_uv = corner;
    gl_Position = vec4(corner * 2.0 - 1.0, 0.0, 1.0);
}