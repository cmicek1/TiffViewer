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

        self.orig_bg = pg.Surface(self.screen.get_size())
        self.orig_bg = self.orig_bg.convert()
        self.curr_bg = self.orig_bg
        self.view_slice(self.orig_bg, self.current_slice)
        pg.display.flip()

    def resize(self, size):
        cap = pg.display.get_caption()
        self.screen = pg.display.set_mode(size, pg.RESIZABLE, BIT_DEPTH)
        pg.display.set_caption(cap[0])
        self.curr_bg = pg.transform.scale(self.orig_bg, size)
        self.screen.blit(self.curr_bg, (0, 0))

    def scroll(self, direction):
        if direction == 'up' and self.current_slice > 0:
            self.current_slice -= 1
            self.view_slice(self.curr_bg, self.current_slice)
        elif direction == 'down'and self.current_slice < self.stack.maxz:
            self.current_slice += 1
            self.view_slice(self.curr_bg, self.current_slice)

    def view_slice(self, background, z):
        imarray = self.stack.getarray[z]
        if imarray.shape != background.get_size():
            bgsurf = pg.Surface(imarray.shape, depth=BIT_DEPTH)
            pg.surfarray.blit_array(bgsurf, imarray)
            pg.transform.scale(bgsurf, background.get_size())
            self.screen.blit(bgsurf, (0, 0))
            self.curr_bg = bgsurf
        else:
            pg.surfarray.blit_array(background, imarray)
            self.screen.blit(background, (0, 0))
        self.current_slice = z
