from library.scrollphat.IS31FL3730 import I2cConstants
import sys
import subprocess
import tempfile
from collections import namedtuple
import pickle
import os

Command = namedtuple('Command', ['cmd', 'vals'])


class SMBus:
    def __init__(self, dummy):
        self.constants = I2cConstants()
        self.constants.CMD_SET_PIXELS = 0x01

        self.pipe_name = tempfile.NamedTemporaryFile().name
        os.mkfifo(self.pipe_name)
        self.sdl_phat_process = subprocess.Popen(
            [sys.executable, 'sdl_phat.py', self.pipe_name])
        self.pipe = open(self.pipe_name, 'wb')

    def write_i2c_block_data(self, addr, cmd, vals):
        assert addr == self.constants.I2C_ADDR

        assert cmd in [self.constants.CMD_SET_PIXELS, self.constants.CMD_SET_MODE,
                       self.constants.CMD_SET_BRIGHTNESS]

        if cmd == self.constants.CMD_SET_MODE:
            assert len(vals) == 1
            assert vals[0] == self.constants.MODE_5X11
        elif cmd == self.constants.CMD_SET_BRIGHTNESS:
            assert len(vals) == 1
        elif cmd == self.constants.CMD_SET_PIXELS:
            assert len(vals) == 12
            assert vals[-1] == 0xFF

        try:
            pickle.dump(Command(cmd=cmd, vals=vals), self.pipe)
            self.pipe.flush()
        except OSError:
            print('lost connection with SDL phat')
            sys.exit(-1)
