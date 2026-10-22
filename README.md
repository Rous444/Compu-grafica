# Rays — Motor gráfico básico con raycasting

Parcial 2026 de **Computación Gráfica** · Universidad Católica de Córdoba (UCC)

**Autores:** Franco Castellani y Joaquín Martínez

Motor gráfico 3D escrito en Python que dibuja una escena con rasterización en la GPU (OpenGL) y detecta qué objeto hay bajo el cursor lanzando rayos desde la cámara. El proyecto se construye de forma incremental, módulo a módulo, siguiendo la guía de la cátedra.

---

## Qué hace

La escena tiene una cámara en perspectiva, un cubo de ladrillos que gira, un cubo de chapa que sube y baja, y un piso de baldosas.

- **Rasterización con OpenGL** (ModernGL): pipeline con vertex y fragment shader.
- **Transformaciones MVP**: matrices de modelo, vista y proyección.
- **Texturas**: color base, repetición (wrapping), mipmaps y filtrado trilineal.
- **Iluminación**: luz direccional con modelo difuso de Lambert y brillo especular de Blinn-Phong.
- **Normal mapping**: relieve en las superficies sin agregar geometría (espacio tangente, matriz TBN).
- **Animación**: comportamientos (`Spin`, `Oscillate`) que modifican el `Transform` en cada actualización, independientes de los FPS.
- **Raycasting**: rayo generado desde la cámara a través del cursor, con intersección contra hitboxes y selección del objeto más cercano.
- **Hitboxes**: AABB (método de slabs), OBB (rayo llevado al espacio local) e intersección rayo-plano para el piso.

## Estado del proyecto

| Módulo | Contenido | Estado |
|---|---|---|
| 01 | Motor Gráfico Básico | Completo |
| 02 | Texturas e Iluminación | Completo |
| 03 | Raycasting | Completo |
| 04 | Raytracing por CPU | Pendiente |
| 05 | Raytracing por GPU | Pendiente |
| 06 | Pathtracing (grupal) | Pendiente |

## Requisitos

- Python 3.10 o superior
- Una GPU con soporte para OpenGL 3.3
- Dependencias: `pyglet`, `moderngl`, `pyglm`

## Instalación y ejecución

Desde PowerShell (Windows):

```powershell
cd rays
python -m venv .venv
.venv\Scripts\activate
pip install pyglet moderngl pyglm
python main.py
```

En macOS o Linux, el entorno virtual se activa con `source .venv/bin/activate`.

> `main.py` hay que ejecutarlo **desde la carpeta `rays/`**: los imports (`domain`, `infrastructure`) y las rutas de texturas se resuelven a partir de ahí.

## Uso

| Acción | Resultado |
|---|---|
| Click izquierdo sobre un objeto | Muestra u oculta su hitbox (caja verde) y escribe en la consola su nombre y la distancia del impacto |
| Click izquierdo sobre el fondo | La consola indica `Nada bajo el cursor` |
| Redimensionar la ventana | La cámara y el viewport se ajustan al nuevo aspect ratio |

Cosas para probar:

- Activar el hitbox del cubo rojo y ver cómo gira pegado al objeto (OBB).
- Activar el hitbox del piso: es su contorno.
- Hacer click en el fondo, en el espacio donde antes había una esquina de la caja AABB: ya no selecciona el cubo.

## Arquitectura

El proyecto separa **qué es una escena** de **cómo se dibuja**:

- `domain/` es matemática pura. No conoce OpenGL ni Pyglet. Acá viven la cámara, las entidades, las transformaciones, los materiales, la luz, los rayos y las intersecciones.
- `infrastructure/` es la tecnología concreta: la ventana de Pyglet, los shaders y todo lo que toca ModernGL.
- El puente entre ambas es el contrato `Renderer` (`domain/renderer.py`), un `Protocol` con los métodos `render(scene)` y `resize(width, height)`. Cualquier clase que lo cumpla puede dibujar la escena sin que la ventana lo note. Por eso el `HitboxOverlay` y el `RasterRenderer` conviven, y por eso más adelante se pueden sumar renderers de raytracing sin tocar la escena.

```
rays/
├── main.py                 # Único archivo que conoce todas las piezas
├── demo_scene.py           # Arma la escena: cámara, cubos y piso
├── assets/textures/        # Texturas de color base (_base) y relieve (_normal)
├── parcial/capturas/       # Capturas de pantalla de cada paso
├── domain/
│   ├── transform.py        # Posición, rotación, escala y matriz de modelo
│   ├── shapes.py           # Box y Rect, en espacio local
│   ├── material.py         # Color, texturas, uv_scale y shininess
│   ├── lighting.py         # Luz direccional
│   ├── camera.py           # Matrices de vista y proyección, y ray_through
│   ├── ray.py              # Rayo: origen + t · dirección
│   ├── intersections.py    # Slabs, OBB, rayo-plano y closest_hit
│   ├── behaviors.py        # Spin y Oscillate
│   ├── entity.py           # Forma, transform, material y comportamientos
│   ├── scene.py            # Cámara, luz, entidades y pick(ray)
│   └── renderer.py         # Contrato Renderer
└── infrastructure/
    ├── pyglet_window.py    # Ventana, loop de actualización y eventos de mouse
    └── opengl/
        ├── shader_loader.py
        ├── meshes.py       # Vértices, normales, UV y tangentes de cada forma
        ├── texture_library.py   # Carga y cache de texturas en la GPU
        ├── raster_renderer.py   # Renderer por rasterización
        ├── hitbox_overlay.py    # Dibuja los hitboxes con líneas
        └── shaders/        # raster.vert/.frag y hitbox.vert/.frag
```

## Cómo funciona el raycasting

1. **Del click al rayo.** `Camera.ray_through(u, v)` pasa la posición del mouse a coordenadas normalizadas (NDC), la ajusta por el FOV vertical y el aspect ratio, arma la dirección en el espacio de la cámara y la lleva al mundo con la inversa de la matriz de vista.
2. **Del mundo al espacio local.** Para cada entidad se aplica la inversa de su matriz de modelo al rayo. En su espacio local, el cubo siempre es la caja de -1 a 1 y el piso siempre es el plano `y = 0`. La dirección local **no se normaliza**, para que la distancia `t` sea la misma en el espacio local y en el mundo y se pueda comparar entre objetos.
3. **Intersección.** El cubo usa el método de slabs contra su caja local (OBB). El piso resuelve la ecuación del rayo contra el plano y se recorta al cuadrado de -1 a 1.
4. **El más cercano.** `closest_hit` recorre todas las entidades y se queda con la de menor distancia.

## Capturas

Las capturas de cada paso están en [`rays/parcial/capturas/`](rays/parcial/capturas), nombradas con el número de paso (`paso00.png`, `paso01.png`, …). En todas se ve el título de la ventana.

## Tecnologías

- [Python](https://www.python.org/)
- [Pyglet](https://pyglet.org/): ventana, eventos y carga de imágenes
- [ModernGL](https://github.com/moderngl/moderngl): contexto y llamadas a OpenGL
- [PyGLM](https://github.com/Zuzu-Typ/PyGLM): vectores, matrices y transformaciones
- GLSL 3.30 para los shaders
