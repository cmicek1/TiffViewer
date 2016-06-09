import os
import pygame as pg
import tiffstack as ts
import viewer
import Tkinter as Tk
import tkFileDialog


class StackBrowser:
    def __init__(self):
        # self.open_stacks = []
        self.viewers = []  # if at some point we port to another library

        root = Tk.Tk()
        root.withdraw()
        fpath = tkFileDialog.askopenfilename(
            initialdir=os.path.expanduser('~/Desktop'))
        t = ts.TiffStack(fpath)
        v = viewer.Viewer(t)
        # self.open_stacks.append(t)
        self.viewers.append(v)

    def _handle_events(self, events):
        for event in events:
            if event.type == pg.QUIT:
                pg.display.quit()
                quit(0)
            elif event.type == pg.VIDEORESIZE:
                (w, h) = event.dict['size']
                (w0, h0) = self.viewers[0].background.get_size()
                if w != w0:
                    h = h0 * w / w0
                else:
                    if h != h0:
                        w = h * w0 / h0

                self.viewers[0].resize((w, h))

    def start(self):
        while True:
            self._handle_events(pg.event.get())
            pg.display.flip()


def main():
    browser = StackBrowser()
    browser.start()


if __name__ == '__main__':
    main()
