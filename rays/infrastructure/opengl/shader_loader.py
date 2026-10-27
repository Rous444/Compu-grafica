import re
from pathlib import Path

import moderngl

SHADERS_DIRECTORY = Path(__file__).parent / "shaders"
INCLUDE_PATTERN = re.compile(r'^[ \t]*#include[ \t]+"([^"]+)"[ \t]*$', re.MULTILINE)


def load_program(context: moderngl.Context, vertex_name: str, fragment_name: str | None = None) -> moderngl.Program:
    """Compila un programa con nombre.vert y nombre.frag. Si se indica otro fragment, se usa ese."""
    return context.program(
        vertex_shader=load_source(f"{vertex_name}.vert"),
        fragment_shader=load_source(f"{fragment_name or vertex_name}.frag"),
    )


def load_compute(context: moderngl.Context, name: str) -> moderngl.ComputeShader:
    return context.compute_shader(load_source(f"{name}.comp"))


def load_source(relative_path: str) -> str:
    return _resolve_includes(SHADERS_DIRECTORY / relative_path, frozenset())


def _resolve_includes(path: Path, include_chain: frozenset[Path]) -> str:
    """Reemplaza cada línea #include "archivo" por el contenido de ese archivo, de forma recursiva."""
    if path in include_chain:
        raise ValueError(f"Circular include: {path.name}")
    source = path.read_text(encoding="utf-8")

    def replace(match: re.Match) -> str:
        return _resolve_includes(SHADERS_DIRECTORY / match.group(1), include_chain | {path})

    return INCLUDE_PATTERN.sub(replace, source)