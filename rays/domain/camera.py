import math
from dataclasses import dataclass, field

from pyglm import glm

from domain.ray import Ray

@dataclass
class Camera:
    position: glm.vec3
    target: glm.vec3
    up: glm.vec3 = field(default_factory=lambda: glm.vec3(0.0, 1.0, 0.0))
    vertical_fov_degrees: float = 45.0
    aspect_ratio: float = 16.0 / 9.0
    near: float = 0.1
    far: float = 100.0

    def view_matrix(self) -> glm.mat4:
        return glm.lookAt(self.position, self.target, self.up)

    def projection_matrix(self) -> glm.mat4:
        return glm.perspective(glm.radians(self.vertical_fov_degrees), self.aspect_ratio, self.near, self.far)

    def resize(self, width: int, height: int) -> None:
        if height > 0:
            self.aspect_ratio = width / height
    
    def tan_half_fov(self) -> float:
            """Mitad de la altura que ve la cámara en un plano a distancia 1."""
            return math.tan(glm.radians(self.vertical_fov_degrees) / 2.0)
    
    def ray_through(self, u: float, v: float) -> Ray:
        """Rayo que sale de la cámara y pasa por el punto (u, v) de la pantalla.

        u y v van de 0 a 1, con (0, 0) en la esquina inferior izquierda.
        """
        # 1. De [0, 1] a NDC [-1, 1].
        ndc_x = 2.0 * u - 1.0
        ndc_y = 2.0 * v - 1.0
        # 2. Ajuste por la apertura de la cámara. El FOV es vertical, así que el aspect ratio
        #    solo estira el eje X.
        tan_half_fov = self.tan_half_fov()
        x_camera = ndc_x * tan_half_fov * self.aspect_ratio
        y_camera = ndc_y * tan_half_fov
        # 3. Dirección en el espacio de la cámara, que mira hacia -Z. w = 0 porque es una dirección.
        direction_camera = glm.vec4(x_camera, y_camera, -1.0, 0.0)
        # 4. Del espacio de la cámara al mundo, con la inversa de la matriz de vista.
        direction_world = glm.vec3(glm.inverse(self.view_matrix()) * direction_camera)
        return Ray(self.position, direction_world)

    
    