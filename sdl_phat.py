#! python3
import sys
import sdl2
import sdl2.ext
import os
import errno
import pickle
from smbus import Command 
from library.scrollphat.IS31FL3730 import I2cConstants


ROWS = 5
COLUMNS = 11
PIXELS_PER_LED = 100
WINDOW_WIDTH_PX = PIXELS_PER_LED * COLUMNS
WINDOW_HEIGHT_PX = PIXELS_PER_LED * ROWS


class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    def render(self, components):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super(SoftwareRenderer, self).render(components)


class Pixel:
    def __init__(self, world, sprite_factory, pos_x, pos_y):
        self.entity = sdl2.ext.Entity(world)
        self.sprite_factory = sprite_factory
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.set_brightness(0)        

    def set_brightness(self, b):
        self.entity.sprite = self.sprite_factory.from_color(sdl2.ext.Color(b, b, b), size=(PIXELS_PER_LED, PIXELS_PER_LED))
        self.entity.sprite.position = (self.pos_x, self.pos_y)


class SDLPhat:
    def __init__(self):
        self.brightness = 255
        self.fifo = None
        self.constants = I2cConstants()
        self.constants.CMD_SET_PIXELS = 0x01

        sdl2.ext.init()
        self.window = sdl2.ext.Window("pHATmulator", size=(WINDOW_WIDTH_PX, WINDOW_HEIGHT_PX))
        self.window.show()

        self.world = sdl2.ext.World()

        self.world.add_system(SoftwareRenderer(self.window))

        self.sprite_factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

        self.pixels = [None] * COLUMNS

        for col in range(COLUMNS):
            self.pixels[col] = [None] * ROWS
            for row in range(ROWS):
                x = PIXELS_PER_LED * col
                y = PIXELS_PER_LED * row
                self.pixels[col][row] = Pixel(self.world, self.sprite_factory, x, y)

        self.world.process()

    def set_brightness(self, brightness):
        self.brightness = brightness if brightness > 100 else 100

    def set_pixels(self, vals):
        for col in range(COLUMNS):
            for row in range(ROWS):
                if vals[col] & (1 << row):
                    self.pixels[col][row].set_brightness(self.brightness)
                else:
                    self.pixels[col][row].set_brightness(0)

    def handle_command(self, command):
        if command.cmd == self.constants.CMD_SET_BRIGHTNESS:
            assert len(command.vals) == 1
            self.set_brightness(command.vals[0])
        elif command.cmd == self.constants.CMD_SET_PIXELS:
            assert len(command.vals) == 12
            assert command.vals[-1] == 0xFF
            self.set_pixels(command.vals)

    def run_from_fifo(self, fifo_name):
        running = True

        while running:
            if not self.fifo:
                self.fifo = open(fifo_name, 'rb')

            if self.fifo:
                try:
                    self.handle_command(pickle.load(self.fifo))
                except OSError as err:
                    if err.errno not in [errno.EAGAIN, errno.EWOULDBLOCK]:
                        raise
                except EOFError:
                    running = False
           
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    running = False
                elif event.type == sdl2.SDL_KEYDOWN:
                    if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                        running = False
                        
            self.window.refresh()
            self.world.process()


if __name__ == "__main__":
    print('starting SDL pHATmulator')
    dl_phat = SDLPhat()

    if len(sys.argv) != 2:
        print('need to specify fifo name')
        sys.exit(1)

    dl_phat.run_from_fifo(sys.argv[1])
