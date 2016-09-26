import numpy as np
import PyQt4.QtCore as qc
import PyQt4.QtGui as qg
import tiffstack as ts
import nodedb as nd
import edgedb as ed
import slabdb as sd


class MainWindow(qg.QMainWindow):
    def __init__(self):
        qg.QMainWindow.__init__(self)
        self.setWindowTitle('StackBrowser')
