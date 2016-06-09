import pygame as pg

BIT_DEPTH = 8


class Viewer:
    def __init__(self, stack, caption="Stack Browser"):
        self.stack = stack
        self.current_slice = 0
        pg.init()
        imarray = self.stack.getarray
        sz_to_use = tuple([imarray.shape[1], imarray.shape[2]])
        self.screen = pg.display.set_mode(sz_to_use, pg.RESIZABLE,
                                          BIT_DEPTH)
        pg.display.set_caption(caption)

        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.view_slice(self.background, self.current_slice)
        pg.display.flip()

    def resize(self, size):
        cap = pg.display.get_caption()
        self.screen = pg.display.set_mode(size, pg.RESIZABLE, BIT_DEPTH)
        pg.display.set_caption(cap[0])
        newbg = pg.transform.scale(self.background, size)
        self.screen.blit(newbg, (0, 0))

    def view_slice(self, background, z):
        pg.surfarray.blit_array(background, self.stack.getarray[z])
        self.screen.blit(background, (0, 0))
        self.current_slice = z
