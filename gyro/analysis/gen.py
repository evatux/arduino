#!/usr/bin/python3

import math
import random
import sys
import time

def n_steps(time_start, time_stop, dt):
    return int((time_stop - time_start) / dt)

def gen_numbers(time_start, time_stop, dt):
    for i in range(n_steps(time_start, time_stop, dt)):
        t = time_start + i * dt
        vals = (math.sin(0.1 * t), math.cos(0.2 * t + 0.1), 0.5)
        print("%.2f  %.2f  %.2f" % vals, flush=True)

def gen(sleep_min=0.5, sleep_max=4, dt=0.2):
    last_time = 0
    cur_time = 0
    while True:
        sleep_time = random.random() * (sleep_max - sleep_min) + sleep_min
        time.sleep(sleep_time)
        cur_time += sleep_time
        gen_numbers(last_time, cur_time, dt)
        last_time += n_steps(last_time, cur_time, dt) * dt

def main():
    gen(sleep_min=0.1, sleep_max=0.1, dt=0.1)

if __name__ == '__main__':
    main()
