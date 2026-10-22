import moderngl

from infrastructure.opengl.shader_loader import load_program

IMAGE_UNIT = 0


class ScreenQuad:
    """Muestra una textura ocupando toda la ventana: la "pantalla virtual" donde dibujan los rayos."""

    def __init__(self, context: moderngl.Context) -> None:
        self._context = context
        self._program = load_program(context, "screen")
        # Sin buffers: el vertex shader calcula las esquinas a partir de gl_VertexID.
        self._vertex_array = context.vertex_array(self._program, [])

    def draw(self, texture: moderngl.Texture) -> None:
        self._context.disable(moderngl.DEPTH_TEST)
        texture.use(location=IMAGE_UNIT)
        self._program["u_image"] = IMAGE_UNIT
        self._vertex_array.render(mode=moderngl.TRIANGLE_STRIP, vertices=4)