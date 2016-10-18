import sys, os
import numpy as np
import PyQt4.QtCore as qc
import PyQt4.QtGui as qg
import stackbrowserQtUI as ui
import tiffstack as ts
import nodedb as nd
import edgedb as ed
import slabdb as sd
import Tkinter as Tk
import tkFileDialog


class MainWindow(qg.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        setter = ui.Ui_MainWindow()
        ui.Ui_MainWindow.setupUi(setter, self)
        action_open = setter.action_Open

        action_open.triggered.connect(lambda: self.click_handler('open'))

    def click_handler(self, handle, *args):
        valid_funcs = {'open': self._open}

        valid_funcs[handle](args)

    def _open(self, *args):
        root = Tk.Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        fpath = tkFileDialog.askopenfilename(
            initialdir=os.path.expanduser('~/Desktop'))
        self.stack = ts.TiffStack(fpath)


def main():
    app = qg.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == '__main__':
    main()