import sys
import numpy as np
import PyQt4.QtCore as qc
import PyQt4.QtGui as qg
import tiffstack as ts
import nodedb as nd
import edgedb as ed
import slabdb as sd
import stackbrowserQtUI as ui


class MainWindow(qg.QMainWindow):
    def __init__(self):
        qg.QMainWindow.__init__(self)
        setter = ui.Ui_MainWindow()
        ui.Ui_MainWindow.setupUi(setter, self)


def main():
    app = qg.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == '__main__':
    main()