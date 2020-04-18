import sys
import sdl2
import sdl2.ext
import time
import threading

ROWS = 5
COLUMNS = 11
PIXELS_PER_LED = 100
WINDOW_WIDTH_PX=PIXELS_PER_LED * COLUMNS
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


    def pump(self):
        print('pump')
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                raise Exception('boom')
            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                    raise Exception('bam')
                else:
                    self.pixels[4][3].set_brightness(128)
            self.world.process()

        sdl2.SDL_Delay(10)

        self.window.refresh()

if __name__ == "__main__":
    dl_phat = SDLPhat()
    while True:
        time.sleep(1)
        dl_phat.pump()