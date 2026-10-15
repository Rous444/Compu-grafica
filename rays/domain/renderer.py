from typing import Protocol

from domain.scene import Scene


class Renderer(Protocol):
    def render(self, scene: Scene) -> None: ...

    def resize(self, framebuffer_width: int, framebuffer_height: int) -> None: ...
