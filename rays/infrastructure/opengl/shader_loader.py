from pathlib import Path

import moderngl

SHADERS_DIRECTORY = Path(__file__).parent / "shaders"


def load_program(context: moderngl.Context, name: str) -> moderngl.Program:
    return context.program(
        vertex_shader=(SHADERS_DIRECTORY / f"{name}.vert").read_text(encoding="utf-8"),
        fragment_shader=(SHADERS_DIRECTORY / f"{name}.frag").read_text(encoding="utf-8"),
    )
