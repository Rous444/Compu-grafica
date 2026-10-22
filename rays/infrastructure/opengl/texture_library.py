from pathlib import Path

import moderngl
import pyglet

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WHITE_TEXEL = bytes((255, 255, 255, 255))
FLAT_NORMAL_TEXEL = bytes((128, 128, 255, 255))


class TextureLibrary:
    """Carga cada imagen una sola vez y la guarda en la memoria de la GPU, indexada por su ruta."""

    def __init__(self, context: moderngl.Context) -> None:
        self._context = context
        self._textures: dict[str, moderngl.Texture] = {}
        self._defaults = {
            "base": self._solid_texture(WHITE_TEXEL),
            "normal": self._solid_texture(FLAT_NORMAL_TEXEL),
        }

    def texture(self, relative_path: str | None, kind: str) -> moderngl.Texture:
        if relative_path is None:
            return self._defaults[kind]
        if relative_path not in self._textures:
            self._textures[relative_path] = self._load(relative_path)
        return self._textures[relative_path]

    def _load(self, relative_path: str) -> moderngl.Texture:
        image = pyglet.image.load(str(PROJECT_ROOT / relative_path)).get_image_data()
        data = image.get_data("RGBA", image.width * 4)
        texture = self._context.texture((image.width, image.height), 4, data)
        texture.build_mipmaps()
        texture.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
        return texture

    def _solid_texture(self, texel: bytes) -> moderngl.Texture:
        return self._context.texture((1, 1), 4, texel)