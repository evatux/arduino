#!/usr/bin/python3

import sys
import math
import time
import moderngl
import numpy
from pyrr import matrix44
import moderngl_window as mglw

import core
import math_utils

class Line:
    def __init__(self, ctx, y, color=(1.0, 1.0, 1.0)):
        self.ctx = ctx
        data = numpy.array([-1., y, 1., y], dtype='f4')
        self.buffer = self.ctx.buffer(reserve=1024)
        self.buffer.write(data.tostring())
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_position;
            void main() { gl_Position = vec4(in_position, 0.0, 1.0); }
            """,
            fragment_shader="""
            #version 330
            out vec4 outColor;
            void main() { outColor = vec4(%g, %g, %g, 1.0); }
            """ % color,
        )
        self.vao = self.ctx.vertex_array(
            self.program, [(self.buffer, '2f', 'in_position')],)

    def render(self):
        self.vao.render(vertices=2, mode=moderngl.LINE_STRIP)


class Points:
    def __init__(self, ctx, raw_data, what, idx, color=(1.0, 1.0, 1.0)):
        self.ctx = ctx
        self.raw_data = raw_data
        self.what = what
        self.idx = idx
        self.data = numpy.array([], dtype='f4') # drawn points
        self.last_offset = 0

        self.buffer = self.ctx.buffer(reserve=1024 * 8)  # 8 bytes for a 2f
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_position;
            uniform mat4 model_matrix;
            uniform mat4 scale_matrix;
            void main() { gl_Position = scale_matrix * model_matrix * vec4(in_position, 0.0, 1.0); }
            """,
            fragment_shader="""
            #version 330
            out vec4 outColor;
            void main() { outColor = vec4(%g, %g, %g, 1.0); }
            """ % color,
        )
        self.vao = self.ctx.vertex_array(
            self.program, [(self.buffer, '2f', 'in_position')],)

    def render(self):
        time = 0
        if self.last_offset > 1:
            time = self.raw_data['time'][self.last_offset - 1] - 0.5
        self.program['model_matrix'].write(
                matrix44.create_from_translation((-time, 0, 0), dtype='f4'))
        self.program['scale_matrix'].write(
                matrix44.create_from_scale((1./10, 1, 1), dtype='f4'))
        self.vao.render(vertices=self.last_offset, mode=moderngl.LINE_STRIP)

    @property
    def byte_size(self):
        return len(self.data) * 4

    def add(self):
        old_data_size = self.byte_size

        new_len = min(len(self.raw_data['time']),
                len(self.raw_data[self.what][self.idx]))
        new = numpy.stack(
                (
                    self.raw_data['time'][self.last_offset : new_len],
                    self.raw_data[self.what][self.idx][self.last_offset : new_len],
                ), axis=-1).astype('f4').flatten()
        self.data = numpy.append(self.data, new)
        self.last_offset = new_len

        resized = False
        # Keep doubling the buffer size until we reach an acceptable size
        while self.byte_size >= self.buffer.size:
            resized = True
            self.buffer.orphan(self.buffer.size * 2)

        if resized:
            self.buffer.write(self.data.tostring())
        else:
            self.buffer.write(new.tostring(), offset=old_data_size)


class GrowingBuffers(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "Buffer Resize / Batch Draw"
    window_size = 1900, 1000
    aspect_ratio = 2.0
    resizable = True
    samples = 2

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.n_inputs = 3
        self.data = {
            'time': numpy.array([]),
            'raw': [numpy.array([]), ] * self.n_inputs,
            'proc': [numpy.array([]), ] * self.n_inputs,
        }
        self.tracker = core.Tracker(self.data, n_inputs=self.n_inputs)
        self.points = (
                Points(self.ctx, self.data, 'proc', 0, color=(0., 1., 0.)),
                # Points(self.ctx, self.data, 'proc', 1, color=(0., 0., 1.)),
                Points(self.ctx, self.data, 'proc', 2, color=(1., 0., 0.)),
                )
        self.lines = (
                Line(self.ctx, -1., color=(1., 1., 1.)),
                Line(self.ctx, 0., color=(1., 1., 1.)),
                Line(self.ctx, 1., color=(1., 1., 1.)),
                )
        self.norm = numpy.array([10., ] + [1., ] * 2)
        self.norm /= self.norm.sum()

        self.v = numpy.array([0., 0., -1.])
        self.compute_Q()

    @classmethod
    def run(cls):
        mglw.run_window_config(cls)

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys
        if action == keys.ACTION_PRESS:
            if key == keys.N:
                self.compute_Q()

    def compute_Q(self):
        self.Q = math_utils.find_Q(self.v)

    def post_process(self, processed):
        n_end = len(self.data['raw'][self.n_inputs - 1])
        n_start = n_end - processed
        for p in range(n_start, n_start + processed):
            v = numpy.array([
                    [self.data['raw'][i][max(p - j, 0)] for j in range(len(self.norm))]
                    for i in range(self.n_inputs)
                ])
            v = v.dot(self.norm)
            v /= math.sqrt(v.dot(v))
            self.v = v

            v = self.Q.dot(v)

            self.data['proc'][0] = numpy.append(self.data['proc'][0],
                    math.sqrt(v[0] * v[0] + v[1] * v[1]))
            # self.data['proc'][1] = numpy.append(self.data['proc'][1], v[1])
            self.data['proc'][2] = numpy.append(self.data['proc'][2], v[2])

    def render(self, time_now, frametime):
        processed = self.tracker.update(timeout=0.01)
        self.post_process(processed)

        # render
        for p in self.points:
            p.add()
            p.render()
        for l in self.lines:
            l.render()


if __name__ == '__main__':
    GrowingBuffers.run()
