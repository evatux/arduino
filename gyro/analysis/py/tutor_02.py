import math
import time
import numpy
import random

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

T = 0
W, H = 1000, 400

def graph(t):
    vertexBuffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertexBuffer)

    _X = numpy.arange(W, dtype='float32')
    _Y = H // 2 * (1. + numpy.cos(4 * 2 * 3.1314 / W * _X + t))
    _Z = numpy.empty(_X.size * 2, dtype = _X.dtype)
    _Z[0::2] = _X
    _Z[1::2] = _Y
    glBufferData(GL_ARRAY_BUFFER, _Z.tostring(), GL_STATIC_DRAW)
    # glVertexAttribPointer(0, 10, GL_FLOAT, GL_FALSE, 20, 0)

    # glEnableClientState(GL_VERTEX_ARRAY)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glBindBuffer(GL_ARRAY_BUFFER, vertexBuffer)
    glVertexPointer(2, GL_FLOAT, 0, 0)
    glColor3f(1.0, 0.0, 0.0)
    glDrawArrays(GL_LINE_STRIP, 0, W)
    glBindVertexArray(0)
    print("here ", _Z[0:10])

    # glBegin(GL_LINE_STRIP)
    # glColor3f(1.0, 0.0, 0.0)
    # for i in range(0, W):
    #    glVertex2f(i, H // 2 * (1. + math.sin(4 * 2 * 3.1415 / W * i + t)))
    # glEnd()


def iterate():
    glViewport(0, 0, W, H)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, W, 0.0, H, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

def showScreen():
    global T
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    # square()
    graph(T)
    glutSwapBuffers()
    time.sleep(1)
    T += 0.1

glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(W, H)
glutInitWindowPosition(10, 10)
wind = glutCreateWindow("OpenGL Coding Practice")
glutDisplayFunc(showScreen)
glutIdleFunc(showScreen)
glutMainLoop()
