import math
import struct
import random
import moderngl
from pyrr import matrix44
from ported._example import Example


SAMPLES_PER_SEC = 1000


class Points:
    def __init__(self, ctx, num_points, color=(1.0, 1.0, 1.0), offset=0, speed=1):
        self.points = []
        self.ctx = ctx
        self.buffer = self.ctx.buffer(reserve=num_points * 12)  # 12 bytes for a 3f
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec3 in_position;
            uniform mat4 model_matrix;
            void main() { gl_Position = model_matrix * vec4(in_position, 1.0); }
            """,
            fragment_shader="""
            #version 330
            out vec4 outColor;
            void main() { outColor = vec4(%g, %g, %g, 1.0); }
            """ % color,
        )
        self.vao = self.ctx.vertex_array(
            self.program, [(self.buffer, '3f', 'in_position')],)
        self.offset = offset
        self.speed = speed

    def render(self, time):
        self.program['model_matrix'].write(
                matrix44.create_from_translation((-time, 0, 0), dtype='f4')
                )
        self.vao.render(vertices=len(self.points) // 3, mode=moderngl.LINE_STRIP)

    @property
    def byte_size(self):
        return len(self.points) * 4

    def add(self, last_time, time):
        resized = False
        old_points_size = self.byte_size
        new = self._gen_random_points(last_time, time)
        self.points = self.points + new

        # Keep doubling the buffer size until we reach an acceptable size
        while self.byte_size > self.buffer.size:
            resized = True
            self.buffer.orphan(self.buffer.size * 2)

        if resized:
            self.buffer.write(struct.pack('{}f'.format(len(self.points)), *self.points))
        else:
            self.buffer.write(struct.pack('{}f'.format(len(new)), *new), offset=old_points_size)

    def _gen_random_points(self, last_time, time):
        new_points = list()
        num = int((time - last_time) * SAMPLES_PER_SEC)
        if num < 1: new_points
        for i in range(num):
            t = last_time + 1. * i / SAMPLES_PER_SEC
            new_points += (t, math.sin(self.speed * t - self.offset), 0)
        return new_points


class GrowingBuffers(Example):
    gl_version = (3, 3)
    title = "Buffer Resize / Batch Draw"
    window_size = 720, 720
    aspect_ratio = 1.0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.points = (
                Points(self.ctx, 12 * 10, color=(1.0, 0.0, 0.0), offset=0.00, speed=0.75),
                Points(self.ctx, 12 * 10, color=(0.0, 1.0, 0.0), offset=0.33, speed=1.00),
                Points(self.ctx, 12 * 10, color=(0.0, 0.0, 1.0), offset=0.66, speed=1.25),
                )
        self.last_time = 0

    def render(self, time, frametime):
        for p in self.points:
            p.render(time)
            p.add(self.last_time, time)
        self.last_time = time


if __name__ == '__main__':
    GrowingBuffers.run()
