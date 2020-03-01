import sys
import math
import time
import struct
import random
import moderngl
from pyrr import matrix44
from ported._example import Example


SAMPLES_PER_SEC = 60


real_arr = [[], [], []]
arr = [[], [], []]

def grab_numbers():
    global arr
    idx = 0
    for i in range(10):
        # print(rl)
        try:
            rl = sys.stdin.readline().rstrip().split(' ')
            vec = (float(rl[0]), float(rl[1]), float(rl[2]))
            n = math.sqrt(vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2])
            pos = len(real_arr[0])
            if True:
                for axis in range(0, 3):
                    real_arr[axis].append(vec[axis] / n)
                    RR = 20
                    if pos < RR:
                        arr[axis].append(real_arr[axis][pos])
                    else:
                        x = 0
                        for rr in range(RR):
                            x += real_arr[axis][pos - rr]
                        arr[axis].append(x / RR)
            else:
                arr[0].append(float(rl[0]) / 90)
                arr[1].append(float(rl[1]) / 90)
                arr[2].append(float(rl[2]) / 90)
            print(arr[0][pos] / n, arr[1][pos] / n, arr[2] / n)
            # val = 1. / 15 * (int(rl) % 29 - 15)
            # arr[idx].append(math.sin(3.1415 * val + idx))
        except:
            pass


class Points:
    def __init__(self, ctx, num_points, idx, color=(1.0, 1.0, 1.0)):
        self.points = []
        self.ctx = ctx
        self.buffer = self.ctx.buffer(reserve=num_points * 12)  # 12 bytes for a 3f
        self.idx = idx
        self.last_offset = 0
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

    def render(self):
        time = 1. / SAMPLES_PER_SEC * self.last_offset - 0.5
        self.program['model_matrix'].write(
                matrix44.create_from_translation((-time, 0, 0), dtype='f4'))
        self.vao.render(vertices=len(self.points) // 3, mode=moderngl.LINE_STRIP)

    @property
    def byte_size(self):
        return len(self.points) * 4

    def add(self):
        resized = False
        old_points_size = self.byte_size
        new = self.read_input()
        self.points = self.points + new

        # Keep doubling the buffer size until we reach an acceptable size
        while self.byte_size > self.buffer.size:
            resized = True
            self.buffer.orphan(self.buffer.size * 2)

        if resized:
            self.buffer.write(struct.pack('{}f'.format(len(self.points)), *self.points))
        else:
            self.buffer.write(struct.pack('{}f'.format(len(new)), *new), offset=old_points_size)

    def read_input(self):
        global arr
        offset = self.last_offset
        self.last_offset = len(arr[self.idx % 3])
        if (offset + 60 < self.last_offset):
            self.last_offset = offset + 60
        new_size = self.last_offset - offset
        new_points = list()
        for i in range(new_size):
            tt = 1. / SAMPLES_PER_SEC * (offset + i)
            if self.idx < 3:
                new_points += (tt, arr[self.idx][offset + i], 0)
            elif self.idx == 3:
                new_points += (tt, 0., 0.)
            elif self.idx == 4:
                new_points += (tt, 1., 0.)
            elif self.idx == 5:
                new_points += (tt, -1., 0.)
        return new_points


class GrowingBuffers(Example):
    gl_version = (3, 3)
    title = "Buffer Resize / Batch Draw"
    window_size = 1000, 1000
    aspect_ratio = 1.0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.points = (
                Points(self.ctx, 12 * 10, idx=0, color=(1., 0., 0.)),
                Points(self.ctx, 12 * 10, idx=1, color=(0., 1., 0.)),
                Points(self.ctx, 12 * 10, idx=2, color=(0., 0., 1.)),
                Points(self.ctx, 12 * 10, idx=3, color=(1., 1., 1.)),
                Points(self.ctx, 12 * 10, idx=4, color=(1., 1., 1.)),
                Points(self.ctx, 12 * 10, idx=5, color=(1., 1., 1.)),
                )

    def render(self, time_now, frametime):
        grab_numbers()
        # time.sleep(0.1)
        for p in self.points:
            p.add()
            p.render()


if __name__ == '__main__':
    GrowingBuffers.run()
