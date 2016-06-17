import pygame as pg

BIT_DEPTH = 8
GRAY = (150, 150, 150)
PAN_FACTOR = 20
ZOOM_FACTOR = 1.5


class Viewer:
    """
    A viewer for multi-page TIFF stacks using PyGame for display/interface.
    Currently, PyGame only supports one display at a time.
    """
    def __init__(self, stack, caption="Stack Browser"):
        """
        Opens a PyGame display window for the given stack.

        The current image is stored on a separate Surface from
        the display window so their respective sizes are not
        necessarily linked.

        Note that the program as-is expects 8-bit L images.

        :param stack: A TiffStack of the TIFF file to open.
        :param caption: Caption for the window.

        :type stack: tiffstack.TiffStack
        :type caption: str
        """
        self.stack = stack
        self.curr_w, self.curr_h = 0, 0
        self.current_slice = 0
        pg.init()
        # Use optimal starting size
        sz_to_use = tuple([self.stack.imarray.shape[1], self.stack.imarray.shape[2]])
        self.screen = pg.display.set_mode(sz_to_use, pg.RESIZABLE,
                                          BIT_DEPTH)
        pg.display.set_caption(caption)

        # Create initial background surface
        self.orig_bg = pg.Surface(self.screen.get_size())
        self.orig_bg = self.orig_bg.convert()
        # Now make a copy - this is what will be altered for zoom/
        # resize operations
        self.curr_bg = self.orig_bg
        self.view_slice(self.orig_bg, self.current_slice)
        pg.display.flip()

    def view_slice(self, background, z, size=None):
        """
        Update the view of 'background' to display
        the image at depth 'z'.

        NOTE: This is currently the slowest part of the program, taking
        about ~0.3 seconds. Will try to optimize before adding more
        functionality.

        :param background: The Surface of the current image.
        :param z: The depth of the image to view.

        :type background: pygame.Surface
        :type z: int

        :rtype: None
        """
        if size is None:
            size = background.get_size()
        imarray = self.stack.imarray[z]

        # Check if window has been resized. If so, resize
        # next image to current window size.
        if imarray.shape != background.get_size():
            pg.surfarray.blit_array(self.orig_bg, imarray)
            self.curr_bg = pg.transform.scale(self.orig_bg, size)
            self.screen.fill(GRAY)
            self.screen.blit(self.curr_bg, (self.curr_w, self.curr_h))
        else:
            pg.surfarray.blit_array(background, imarray)
            self.orig_bg = background
            self.screen.fill(GRAY)
            self.screen.blit(background, (self.curr_w, self.curr_h))

        self.current_slice = z

    def resize(self, size):
        """
        Resizes the current image and window to the given size.

        :param size: A tuple of (width, height) representing the
                     new size of the image

        :type size: tuple(int, int)

        :rtype: None
        """
        cap = pg.display.get_caption()
        (old_w, old_h) = self.screen.get_size()
        self.screen = pg.display.set_mode(size, pg.RESIZABLE, BIT_DEPTH)
        pg.display.set_caption(cap[0])
        self.curr_bg = pg.transform.scale(self.orig_bg, size)

        self.screen.fill(GRAY)

        self.curr_w = float(self.curr_w) / old_w * size[0]
        self.curr_h = float(self.curr_h) / old_h * size[1]

        self.screen.blit(self.curr_bg, (self.curr_w, self.curr_h))

    def scroll(self, direction):
        """
        Scroll up or down through the stack, viewing the next
        or previous image.

        :param direction: The direction to scroll.

        :type direction: str in ['up', 'down']

        :rtype: None
        """
        if direction == 'up' and self.current_slice > 0:
            self.current_slice -= 1
            self.view_slice(self.curr_bg, self.current_slice)
        elif direction == 'down' and self.current_slice < self.stack.maxz:
            self.current_slice += 1
            self.view_slice(self.curr_bg, self.current_slice)

    def pan(self, direction):
        """
        Moves the view in the specified direction a distance proportional
        to the PAN_FACTOR.

        :param direction: The direction to pan.

        :type direction: str in ['up', 'down', 'left', 'right']

        :rtype: None
        """
        if direction == 'up':
            self.curr_h += self.screen.get_size()[1] / PAN_FACTOR
            self.screen.fill(GRAY)
            self.screen.blit(self.curr_bg, (self.curr_w, self.curr_h))

        elif direction == 'down':
            self.curr_h -= self.screen.get_size()[1] / PAN_FACTOR
            self.screen.fill(GRAY)
            self.screen.blit(self.curr_bg, (self.curr_w, self.curr_h))

        elif direction == 'left':
            self.curr_w += self.screen.get_size()[1] / PAN_FACTOR
            self.screen.fill(GRAY)
            self.screen.blit(self.curr_bg, (self.curr_w, self.curr_h))

        elif direction == 'right':
            self.curr_w -= self.screen.get_size()[1] / PAN_FACTOR
            self.screen.fill(GRAY)
            self.screen.blit(self.curr_bg, (self.curr_w, self.curr_h))

    def zoom(self, direction):
        to_zoom = pg.mouse.get_pos()
        size = self.curr_bg.get_size()
        if direction == 'center':
            self.curr_w, self.curr_h = 0, 0
            self.view_slice(self.curr_bg, self.current_slice,
                            self.screen.get_size())

        elif direction == 'in':
            self.curr_bg = pg.transform.scale(
                self.orig_bg, tuple(int(_ * ZOOM_FACTOR) for _ in size))
            self.curr_w -= (to_zoom[0] * ZOOM_FACTOR - self.screen.get_size()[0] / 2)
            self.curr_h -= (to_zoom[1] * ZOOM_FACTOR - self.screen.get_size()[1] / 2)
            self.screen.fill(GRAY)
            self.screen.blit(self.curr_bg, (self.curr_w, self.curr_h))

        elif direction == 'out':
            self.curr_bg = pg.transform.scale(
                self.orig_bg, tuple(int(_ / ZOOM_FACTOR) for _ in size))
            self.curr_w -= (to_zoom[0] / ZOOM_FACTOR - self.screen.get_size()[0] / 2)
            self.curr_h -= (to_zoom[1] / ZOOM_FACTOR - self.screen.get_size()[1] / 2)
            self.screen.fill(GRAY)
            self.screen.blit(self.curr_bg, (self.curr_w, self.curr_h))
