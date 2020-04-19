#!/usr/bin/env python

import time

import scrollphat

scrollphat.clear()
print('pixels')
for x in range(11):
    for y in range(5):
        scrollphat.set_pixel(x, y, 1)
        scrollphat.update()
        time.sleep(0.05)
