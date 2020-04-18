#!/usr/bin/env python

import sys
import time

import scrollphat

scrollphat.clear()
print('pixels')
for y in range(5):
    scrollphat.set_pixel(0,y, 1)
    scrollphat.update()
    time.sleep(1)
    print('again')
