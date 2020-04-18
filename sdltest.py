import sys
import sdl2
import sdl2.ext

ROWS = 5
COLUMNS = 11
PIXELS_PER_LED = 100
WINDOW_WIDTH_PX=PIXELS_PER_LED * COLUMNS
WINDOW_HEIGHT_PX = PIXELS_PER_LED * ROWS

WHITE = sdl2.ext.Color(255, 255, 255)

class SoftwareRenderer(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super(SoftwareRenderer, self).__init__(window)

    def render(self, components):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super(SoftwareRenderer, self).render(components)


factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

class Pixel:
    def __init__(self, world, pos_x, pos_y):
        self.entity = sdl2.ext.Entity(world)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.set_brightness(255)        

    def set_brightness(self, b):
        print('setting brightness')
        self.entity.sprite = factory.from_color(sdl2.ext.Color(b, b, b), size=(PIXELS_PER_LED, PIXELS_PER_LED))
        self.entity.sprite.position = (self.pos_x, self.pos_y)



def run():
    sdl2.ext.init()
    window = sdl2.ext.Window("pHATmulator", size=(WINDOW_WIDTH_PX, WINDOW_HEIGHT_PX))
    window.show()

    world = sdl2.ext.World()

    spriterenderer = SoftwareRenderer(window)
    world.add_system(spriterenderer)

    

    pixels = [None] * COLUMNS

    for col in range(COLUMNS):
        pixels[col] = [None] * ROWS
        for row in range(ROWS):
            x = PIXELS_PER_LED * col
            y = PIXELS_PER_LED * row
            print('x:', x, 'y:', y)
            pixels[col][row] = Pixel(world, x, y)

    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
            elif event.type == sdl2.SDL_KEYDOWN:
                print('key')
                pixels[4][3].set_brightness(128)
        world.process()

if __name__ == "__main__":
    sys.exit(run())