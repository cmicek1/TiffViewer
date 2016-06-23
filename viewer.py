import os
import tiffstack as ts
import pygame as pg

GREEN_PALETTE = []
RED_PALETTE = []
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
        make_colors()
        self.open_stacks = []
        self.stack = stack
        self.curr_w, self.curr_h = 0, 0
        self.current_slice = 0
        self._scale = 1
        self._curr_palette = GREEN_PALETTE
        pg.init()
        # Use optimal starting size
        sz_to_use = tuple([self.stack.imarray.shape[1], self.stack.imarray.shape[2]])
        self.screen = pg.display.set_mode(sz_to_use, pg.RESIZABLE,
                                          BIT_DEPTH)
        pg.display.set_caption(caption)
        self.screen.set_palette(self._curr_palette)

        # Create initial background surface
        self.orig_bg = pg.Surface(self.screen.get_size())
        self.orig_bg = self.orig_bg.convert()

        # TODO: Fix colors
        pg.draw.circle(self.orig_bg, (190, 0, 0), (500, 500), 40)

        # Now make a copy - this is what will be altered for zoom/
        # resize operations
        self.curr_bg = self.orig_bg
        self.view_slice(self.orig_bg, self.current_slice)
        self.open_stacks.append(self.stack)
        pg.display.flip()

    def view_slice(self, background, z, size=None):
        """
        Update the view of 'background' to display
        the image at depth 'z'.

        :param background: The Surface of the current image.
        :param z: The depth of the image to view.
        :param size: Tuple of size (w, h) to scale image to (used if resizing a zoomed
                     image)

        :type background: pygame.Surface
        :type z: int
        :type size: tuple(int, int)

        :return: None
        """
        if size is None:
            size = background.get_size()
        imarray = self.stack.imarray[z]

        # Check if window has been resized. If so, resize
        # next image to current window size.
        if imarray.shape != background.get_size():
            pg.surfarray.blit_array(self.orig_bg, imarray)
            self.curr_bg = pg.transform.scale(self.orig_bg, size)
            self.screen.blit(self.curr_bg, (self.curr_w, self.curr_h))
        else:
            pg.surfarray.blit_array(background, imarray)
            self.orig_bg = background
            self.screen.blit(background, (self.curr_w, self.curr_h))

        self.current_slice = z

    def resize(self, size):
        """
        Resizes the current image and window to the given size.

        :param size: A tuple of (width, height) representing the
                     new size of the image

        :type size: tuple(int, int)

        :return: None
        """
        cap = pg.display.get_caption()
        (old_w, old_h) = self.screen.get_size()
        self.screen = pg.display.set_mode(size, pg.RESIZABLE, BIT_DEPTH)
        pg.display.set_caption(cap[0])
        self.screen.set_palette(self._curr_palette)

        if self._scale != 1:
            size2 = (int(size[0] * self._scale), int(size[1] * self._scale))
        else:
            size2 = size
        self.curr_bg = pg.transform.scale(self.orig_bg, size2)

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

        :return: None
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

        :return: None
        """
        if direction == 'up':
            self.curr_h += self.screen.get_size()[1] / PAN_FACTOR
            # TODO: Play around with Rectangles

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
        """
        Zooms the current image about the position of the mouse cursor.

        :param direction: The direction to zoom. 'Center' returns the image
        to a scale of 1 centered about the window center.

        :type direction: str in ['center', 'in', 'out']

        :return: None
        """
        to_zoom = pg.mouse.get_pos()
        size = self.curr_bg.get_size()
        if direction == 'center':
            self.curr_w, self.curr_h = 0, 0
            self._scale = 1
            self.view_slice(self.curr_bg, self.current_slice,
                            self.screen.get_size())

        elif direction == 'in':
            self.curr_bg = pg.transform.scale(
                self.orig_bg, tuple(int(_ * ZOOM_FACTOR) for _ in size))
            self.curr_w = self.curr_w * ZOOM_FACTOR - to_zoom[0] * (ZOOM_FACTOR - 1)
            self.curr_h = self.curr_h * ZOOM_FACTOR - to_zoom[1] * (ZOOM_FACTOR - 1)
            self._scale *= ZOOM_FACTOR
            self.screen.fill(GRAY)
            self.screen.blit(self.curr_bg, (self.curr_w, self.curr_h))

        elif direction == 'out':
            self.curr_bg = pg.transform.scale(
                self.orig_bg, tuple(int(_ / ZOOM_FACTOR) for _ in size))
            self.curr_w = self.curr_w / ZOOM_FACTOR - to_zoom[0] * (1 / ZOOM_FACTOR - 1)
            self.curr_h = self.curr_h / ZOOM_FACTOR - to_zoom[1] * (1 / ZOOM_FACTOR - 1)
            self._scale /= ZOOM_FACTOR
            self.screen.fill(GRAY)
            self.screen.blit(self.curr_bg, (self.curr_w, self.curr_h))

    def change_view(self, direction):
        """
        Change the file seen in the current viewer.

        View either the previous or the next time point,
        if it exists, or switch between channels 1 and
        2.

        NOTE: Expects a working directory of only vascular
        stack TIFFs, alternating between channels 1 and 2,
        named as follows:

        Xyyyymmdd_aANUMALNUMBER_hsHYPERSTACKNUMBER_chCHANNELNUMBER.tif
        ex: X20140516_a153_hs3_ch2.tif

        :param direction: The direction to look, either next
                          or prev.

        :type direction: str in ['next', 'prev']

        :return: None
        """
        dirpath = os.path.dirname(self.stack.directory)
        flist = os.listdir(dirpath)
        curr_index = flist.index(os.path.basename(self.stack.directory))
        fname = None
        new_palette = None
        try:
            # Deal with time point change
            if direction == 'next':
                if curr_index < len(flist) - 3:
                    fname = flist[curr_index + 2]
                else:
                    raise StackOutOfBoundsException(
                        "No future time point (end of hyperstack)"
                    )
            elif direction == 'prev':
                if curr_index > 1:
                    fname = flist[curr_index - 2]
                else:
                    raise StackOutOfBoundsException(
                        "No previous time point (beginning of hyperstack)"
                    )

            # Deal with channel change
            elif direction == '1':
                new_palette = GREEN_PALETTE
                fname = flist[curr_index - 1]
            elif direction == '2':
                new_palette = RED_PALETTE
                fname = flist[curr_index + 1]

        except StackOutOfBoundsException as e:
            print e.args[0]

        if fname is not None:
            for stack in self.open_stacks:
                if stack.fname == fname:
                    self.stack = stack
            if self.stack.fname != fname:
                self.stack = ts.TiffStack(dirpath + '/' + fname)
            self.curr_w, self.curr_h = 0, 0
            if direction == 'next' or direction == 'prev':
                self.current_slice = 0
            self._scale = 1
            self.curr_bg = self.orig_bg
            if new_palette is not None:
                self._curr_palette = new_palette
                self.screen.set_palette(self._curr_palette)
                self.orig_bg.set_palette(self._curr_palette)
                self.curr_bg.set_palette(self._curr_palette)
            self.view_slice(self.curr_bg, self.current_slice)
            self.open_stacks.append(self.stack)


class StackOutOfBoundsException(Exception):
    """
    Extension of Exception to indicate attempts to
    access time points out of range.
    """
    pass


def make_colors():
    """
    Setter for globals x_PALETTE, which are color palettes
    for the display.
    :return: None
    """
    global GREEN_PALETTE
    global RED_PALETTE
    for i in range(256):
        # GREEN_PALETTE.append((0, i, 0))
        # RED_PALETTE.append((i, 0, 0))

        # TODO: Fix this (at some point)
        if i != GRAY[0]:
            GREEN_PALETTE.append((0, i, 0))
            RED_PALETTE.append((i, 0, 0))
        else:
            # This is a bit of a hack, but I couldn't find a way
            # to update the palette of a portion of a surface.
            GREEN_PALETTE.append(GRAY)
            RED_PALETTE.append(GRAY)
