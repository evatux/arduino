#!/usr/bin/python3

import numpy
import re
import select
import sys
import time

class Tracker:
    def __init__(self, data, n_inputs=3, track_time=True, fd=sys.stdin):
        self.fd = fd
        self.n_inputs = n_inputs
        self.track_time = track_time
        self.start_time = time.time()
        self.data = data

    def update(self, timeout=0.05):
        processed = 0
        time_poll_start = time.time()
        time_poll_stop = time_poll_start + timeout
        while True:
            now = time.time()
            time_poll_timeout = time_poll_stop - now
            if (time_poll_timeout <= 0): break;

            while self.fd in \
                    select.select([self.fd], [], [], time_poll_timeout)[0]:
                try:
                    line = self.fd.readline()
                    if line:
                        processed += self.parse_line(line, time.time())
                    else:
                        print('select return eof')
                        sys.exit(0)
                except:
                    pass
        return processed

    def parse_line(self, line, time_stamp):
        parsed = False
        try:
            if re.match(r'^(([0-9.e+-]+)\s*){%d}$' % self.n_inputs, line):
                vec = re.findall(r'([0-9.e+-]+)\s*', line)
                for i in range(self.n_inputs):
                    self.data['raw'][i] = \
                            numpy.append(self.data['raw'][i], float(vec[i]))
                parsed = True
        except:
            pass
        if self.track_time:
            t = time_stamp - self.start_time
            self.data['time'] = numpy.append(self.data['time'], t)
        if not parsed:
            print("@@@ skip line: ", line)
        return parsed


def main():
    n_inputs = 2
    data = {
        'time': numpy.array([]),
        'raw': [numpy.array([]), ] * n_inputs,
    }
    tracker = Tracker(data, n_inputs=n_inputs)
    while True:
        tracker.update()
