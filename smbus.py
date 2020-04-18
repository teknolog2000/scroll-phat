from library.scrollphat.IS31FL3730 import I2cConstants
import logging
import sys
from sdl_phat import SDLPhat

def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)

    root.addHandler(sh)


setup_logging()


class SMBus:
    def __init__(self, dummy):
        self.constants = I2cConstants()
        self.constants.CMD_SET_PIXELS = 0x01
        self.sdl_phat = SDLPhat()

    def write_i2c_block_data(self, addr, cmd, vals):
        assert addr == self.constants.I2C_ADDR

        assert cmd in [self.constants.CMD_SET_PIXELS, self.constants.CMD_SET_MODE,
                       self.constants.CMD_SET_BRIGHTNESS]

        if cmd == self.constants.CMD_SET_MODE:
            assert len(vals) == 1
            assert vals[0] == self.constants.MODE_5X11
        elif cmd == self.constants.CMD_SET_BRIGHTNESS:
            assert len(vals) == 1
            self.sdl_phat.set_brightness(vals[0])
        elif cmd == self.constants.CMD_SET_PIXELS:
            assert len(vals) == 12
            assert vals[-1] == 0xFF
            self.sdl_phat.set_pixels(vals)
        
        self.sdl_phat.pump()

