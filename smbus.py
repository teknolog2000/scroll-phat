from library.scrollphat.IS31FL3730 import I2cConstants
import logging
import sys


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
        self.constants.CMD_OTHER = 0x01
        self.brightness = 255

    def write_i2c_block_data(self, addr, cmd, vals):
        assert addr == self.constants.I2C_ADDR

        assert cmd in [self.constants.CMD_OTHER, self.constants.CMD_SET_MODE,
                       self.constants.CMD_SET_BRIGHTNESS]

        if cmd == self.constants.CMD_SET_MODE:
            assert vals[0] == self.constants.MODE_5X11
            logging.info('set mode')
        elif cmd == self.constants.CMD_SET_BRIGHTNESS:
            assert len(vals) == 1
            self.brightness = vals[0]
            logging.info('set brightness to %d', self.brightness)
        elif cmd == self.constants.CMD_OTHER:
            logging.info('other')
            self.handle_other(vals)

    def handle_other(self, vals):
        pass
