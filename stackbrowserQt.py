import sys, os
import numpy as np
import PyQt4.QtCore as qc
import PyQt4.QtGui as qg
import stackbrowserQtUI as ui
import tiffstack as ts
import Tkinter as Tk
import tkFileDialog


class MainWindow(qg.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        setter = ui.Ui_MainWindow()
        ui.Ui_MainWindow.setupUi(setter, self)
        action_open = setter.action_Open

        action_open.triggered.connect(lambda: self.click_handler('open'))

        self.COLORTABLE = []
        for i in range(256):
            self.COLORTABLE.append(qg.qRgb(i / 4, i, i / 2))

        self.scene = qg.QGraphicsScene()
        self.view = setter.graphicsView
        self.view.setScene(self.scene)

        self.view.fitInView(self.scene.sceneRect(), qc.Qt.KeepAspectRatio)
        self.view.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)

        self.imageLabel = qg.QLabel()
        self.imageLabel.setGeometry(0, 0, 1024, 1024)  # position and size of image

        # Note: palette not guaranteed to be cross-platform
        palette = qg.QPalette()
        palette.setColor(qg.QPalette.Background, qc.Qt.white)
        self.imageLabel.setPalette(palette)

        self.scene.addWidget(self.imageLabel)

        self.leftToolbar = setter.toolBar

        self.list = qg.QTableView(self)
        self.list.setFont(qg.QFont("Arial", 10))
        self.leftToolbar.addWidget(self.list)

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

        a = self.stack.get_slice(0)
        self.image = qg.QImage(a.tostring(), a.shape[0], a.shape[1], qg.QImage.Format_Indexed8)
        self.image.setColorTable(self.COLORTABLE)
        self.imageLabel.setPixmap(qg.QPixmap.fromImage(self.image))

        self.z = 0


def _exit_handler():
    sys.exit(0)


def main():
    app = qg.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.aboutToQuit.connect(_exit_handler)
    return app.exec_()


if __name__ == '__main__':
    main()