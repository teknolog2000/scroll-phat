import sys
try:
    import sdl2
    import sdl2.ext
except ImportError:
    print('sdl2 missing, please do pip install pysdl2')  # todo
    sys.exit(-1)

import errno
import pickle
from library.scrollphat.IS31FL3730 import I2cConstants
import tkinter as tk

import threading

ROWS = 5
COLUMNS = 11
PIXELS_PER_LED = 50
LINE_WIDTH = 5

WINDOW_HEIGHT = PIXELS_PER_LED * ROWS + LINE_WIDTH * (ROWS - 1)
WINDOW_WIDTH = PIXELS_PER_LED * COLUMNS + LINE_WIDTH * (COLUMNS - 1)


class ScrollPhatSimulator:
    def set_pixels(self, vals):
        raise NotImplementedError()

    def set_brightness(self, brightness):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()

    def destroy(self):
        raise NotImplementedError()


class Pixel:
    def __init__(self, world, sprite_factory, pos_x, pos_y):
        self.entity = sdl2.ext.Entity(world)
        self.sprite_factory = sprite_factory
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.set_brightness(0)

    def set_brightness(self, b):
        self.entity.sprite = self.sprite_factory.from_color(
            sdl2.ext.Color(b, b, b), size=(PIXELS_PER_LED, PIXELS_PER_LED))
        self.entity.sprite.position = (self.pos_x, self.pos_y)


class SDLPhatSimulator(ScrollPhatSimulator):
    def __init__(self):
        self.running = True
        sdl2.ext.init()

        self.window = sdl2.ext.Window(
            "pHATmulator", size=(WINDOW_WIDTH, WINDOW_HEIGHT))
        self.window.show()

        self.world = sdl2.ext.World()
        self.world.add_system(sdl2.ext.SoftwareSpriteRenderSystem(self.window))
        self.sprite_factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

        self.pixels = [[0]*ROWS for i in range(COLUMNS)]

        for col in range(COLUMNS):
            for row in range(ROWS):
                self.pixels[col][row] = Pixel(self.world, self.sprite_factory,
                                              (PIXELS_PER_LED + LINE_WIDTH) * col, (PIXELS_PER_LED + LINE_WIDTH) * row)

    def set_pixels(self, vals):
        for col in range(COLUMNS):
            for row in range(ROWS):
                if vals[col] & (1 << row):
                    self.pixels[col][row].set_brightness(255)
                else:
                    self.pixels[col][row].set_brightness(0)

    def destroy(self):
        self.running = False

    def run(self):

        # processor = sdl2.ext.TestEventProcessor()

        # processor.run(self.window)

        while self.running:
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    self.destroy()

            self.window.refresh()
            self.world.process()


class TkPhatSimulator(ScrollPhatSimulator):
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)

        self.root.bind('<Control-c>', self.destroy)

        self.root.title('pHAT')
        self.root.geometry('{}x{}'.format(WINDOW_WIDTH, WINDOW_HEIGHT))
        self.canvas = tk.Canvas(
            self.root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.canvas.config(highlightthickness=0)

        self.running = True

        self.pixels = [[0]*ROWS for i in range(COLUMNS)]

        self.draw_pixels()

    def run(self):
        print('run')
        self.root.mainloop()

    def destroy(self):
        self.running = False

    def draw_pixels(self):
        if not self.running:
            self.root.destroy()
            return

        self.canvas.delete(tk.ALL)
        self.canvas.create_rectangle(
            0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, width=0, fill='black')

        for col in range(COLUMNS):
            for row in range(ROWS):
                x = (PIXELS_PER_LED + LINE_WIDTH) * col
                y = (PIXELS_PER_LED + LINE_WIDTH) * row
                self.canvas.create_rectangle(
                    x, y, x + PIXELS_PER_LED, y + PIXELS_PER_LED, width=0, fill='white' if self.pixels[col][row]
                    else 'black')

        self.canvas.pack()

        self.root.after(10, self.draw_pixels)

    def set_pixels(self, vals):
        for col in range(COLUMNS):
            for row in range(ROWS):
                if vals[col] & (1 << row):
                    self.pixels[col][row] = 1
                else:
                    self.pixels[col][row] = 0


class FifoThead:
    def __init__(self, fifo_name, scroll_phat_simulator):
        self.fifo_name = fifo_name
        self.scroll_phat_simulator = scroll_phat_simulator

        self.constants = I2cConstants()
        self.constants.CMD_SET_PIXELS = 0x01

        self.fifo = None
        self.fifo_thread = threading.Thread(target=self.read_fifo)
        self.fifo_thread.start()

    def read_fifo(self):
        while True:
            if not self.fifo:
                self.fifo = open(self.fifo_name, 'rb')

            try:
                self.handle_command(pickle.load(self.fifo))
            except OSError as err:
                if err.errno not in [errno.EAGAIN, errno.EWOULDBLOCK]:
                    raise
            except Exception as e:
                print(e)
                self.scroll_phat_simulator.destroy()
                break

    def handle_command(self, command):
        if command.cmd == self.constants.CMD_SET_BRIGHTNESS:
            assert len(command.vals) == 1
            self.scroll_phat_simulator.set_brightness(command.vals[0])
        elif command.cmd == self.constants.CMD_SET_PIXELS:
            assert len(command.vals) == 12
            assert command.vals[-1] == 0xFF
            self.scroll_phat_simulator.set_pixels(command.vals)


def main():
    print('starting scroll pHAT simulator')

    if len(sys.argv) != 2:
        print('need to specify fifo name')
        sys.exit(1)

    fifo_name = sys.argv[1]

#    phat = TkPhatSimulator()
    phat = SDLPhatSimulator()
    FifoThead(fifo_name, phat)

    phat.run()


if __name__ == "__main__":
    main()
