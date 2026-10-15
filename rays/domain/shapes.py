from dataclasses import dataclass


class Shape:
    """Geometría básica definida en un espacio local. El tamaño y posición viene del Transform."""


@dataclass(frozen=True)
class Box(Shape):
    """un cubo que va de -1 a 1 en los tres ejes locales."""


@dataclass(frozen=True)
class Rect(Shape):
    """un cuadrado plano que va de -1 a 1 en X y Z, apoyado en y = 0 y mirando hacia +Y"""
