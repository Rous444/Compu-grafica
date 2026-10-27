from pathlib import Path

import moderngl
import pyglet

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WHITE_TEXEL = bytes((255, 255, 255, 255))
FLAT_NORMAL_TEXEL = bytes((128, 128, 255, 255))

ARRAY_LAYER_SIZE = 512
WHITE_LAYER = 0
FLAT_NORMAL_LAYER = 1


def _read_rgba(relative_path: str) -> tuple[int, int, bytes]:
    """Lee una imagen con Pyglet y devuelve su ancho, su alto y sus bytes RGBA (fila de abajo primero)."""
    image = pyglet.image.load(str(PROJECT_ROOT / relative_path)).get_image_data()
    return image.width, image.height, image.get_data("RGBA", image.width * 4)


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
        width, height, data = _read_rgba(relative_path)
        texture = self._context.texture((width, height), 4, data)
        return texture

    def _solid_texture(self, texel: bytes) -> moderngl.Texture:
        return self._context.texture((1, 1), 4, texel)

    def texture_array(self, relative_paths: list[str]) -> tuple[moderngl.TextureArray, dict[str, int]]:
        """Junta todas las imágenes en un texture array: una capa por imagen.

        La capa 0 es blanca y la 1 es la normal plana: las usan los materiales sin imagen.
        Devuelve el array y un diccionario con la capa de cada ruta.
        """
        size = ARRAY_LAYER_SIZE
        layers = [WHITE_TEXEL * size * size, FLAT_NORMAL_TEXEL * size * size]
        layer_of: dict[str, int] = {}
        for relative_path in dict.fromkeys(relative_paths):  # sin repetidos, en orden
            width, height, data = _read_rgba(relative_path)
            if (width, height) != (size, size):
                raise ValueError(f"{relative_path} must be {size}x{size} to fit in the texture array")
            layer_of[relative_path] = len(layers)
            layers.append(data)
        array = self._context.texture_array((size, size, len(layers)), 4, b"".join(layers))
        array.build_mipmaps()
        array.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
        return array, layer_of