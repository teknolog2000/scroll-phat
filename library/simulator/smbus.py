import sys
import subprocess
import tempfile
from collections import namedtuple
import pickle
import os

from scroll_phat_simulator import Cmds

Command = namedtuple('Command', ['cmd', 'vals'])


class SMBus:
    def __init__(self, dummy):
        self.pipe = None
        try:
            self._start_simulator()
        except OSError as e:
            print(e)

    def _start_simulator(self):
        pipe_name = tempfile.NamedTemporaryFile().name
        os.mkfifo(pipe_name)

        print([sys.executable, os.path.dirname(os.path.abspath(__file__)) + '/scroll_phat_simulator.py', pipe_name])
        self.sdl_phat_process = subprocess.Popen(
            [sys.executable, os.path.dirname(os.path.abspath(__file__)) + '/scroll_phat_simulator.py', pipe_name])
        print(self.sdl_phat_process.returncode)
        print('opening', pipe_name)
        self.pipe = open(pipe_name, 'wb')
        print('started')

    def write_i2c_block_data(self, addr, cmd, vals):
        I2C_ADDR = 0x60
        MODE_5X11 = 0b00000011

        assert addr == I2C_ADDR

        parsed_cmd = Cmds(cmd)

        if parsed_cmd == Cmds.CMD_SET_MODE:
            assert len(vals) == 1
            assert vals[0] == MODE_5X11
        elif parsed_cmd == Cmds.CMD_SET_BRIGHTNESS:
            assert len(vals) == 1
        elif parsed_cmd == Cmds.CMD_SET_PIXELS:
            assert len(vals) == 12
            assert vals[-1] == 0xFF

        try:
            pickle.dump(Command(cmd=parsed_cmd, vals=vals), self.pipe)
            self.pipe.flush()
        except OSError:
            print('lost connection with scroll pHAT simulator')
            sys.exit(-1)
