from typing import Protocol, runtime_checkable

from domain.scene import Scene


class Renderer(Protocol):
    def render(self, scene: Scene) -> None: ...

    def resize(self, framebuffer_width: int, framebuffer_height: int) -> None: ...


@runtime_checkable
class ProgressiveRenderer(Renderer, Protocol):
    """Un renderer que promedia muestras entre frames: solo converge si la escena está quieta."""

    @property
    def sample_count(self) -> int: ...
