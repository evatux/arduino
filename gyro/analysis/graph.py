#!/usr/bin/python3

import sys
import math
import time
import struct
import os
import random
import moderngl
import numpy
from pyrr import matrix44
import moderngl_window as mglw

import core


SAMPLES_PER_SEC = 60


class Points:
    def __init__(self, ctx, raw_data, idx, color=(1.0, 1.0, 1.0)):
        self.ctx = ctx
        self.raw_data = raw_data
        self.idx = idx
        self.data = numpy.array([]) # drawn points
        self.last_offset = 0

        self.buffer = self.ctx.buffer(reserve=1024 * 8)  # 8 bytes for a 2f
        self.program = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_position;
            uniform mat4 model_matrix;
            void main() { gl_Position = model_matrix * vec4(in_position, 0.0, 1.0); }
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
        self.vao.render(vertices=self.last_offset, mode=moderngl.LINE_STRIP)

    @property
    def byte_size(self):
        return len(self.data) * 4

    def add(self):
        old_data_size = self.byte_size

        new_len = len(self.raw_data['time'])
        new = numpy.stack(
                (
                    self.raw_data['time'][self.last_offset : new_len],
                    self.raw_data['raw'][self.idx][self.last_offset : new_len],
                ), axis=-1).astype('f4').flatten()
        self.data = numpy.append(self.data, new)
        self.last_offset = new_len

        resized = False
        # Keep doubling the buffer size until we reach an acceptable size
        while self.byte_size > self.buffer.size:
            resized = True
            self.buffer.orphan(self.buffer.size * 2)

        if resized:
            self.buffer.write(self.data.tostring())
        else:
            self.buffer.write(new.tostring(), offset=old_data_size)


class GrowingBuffers(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "Buffer Resize / Batch Draw"
    window_size = 1000, 1000
    aspect_ratio = 1.0
    resizable = True
    samples = 4
    resource_dir = os.path.normpath(os.path.join(__file__, '../data'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        n_inputs = 2
        self.data = {
            'time': numpy.array([]),
            'raw': [numpy.array([]), ] * n_inputs,
        }
        self.tracker = core.Tracker(self.data, n_inputs=n_inputs)
        self.points = (
            Points(self.ctx, self.data, 0, color=(1., 0., 0.)),
            Points(self.ctx, self.data, 1, color=(0., 1., 0.)),
        )

    @classmethod
    def run(cls):
        mglw.run_window_config(cls)

    def render(self, time_now, frametime):
        self.tracker.update(timeout=0.1)
        for p in self.points:
            p.add()
            p.render()


if __name__ == '__main__':
    GrowingBuffers.run()
