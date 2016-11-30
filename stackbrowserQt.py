import sys, os
import numpy as np
import PyQt4.QtCore as qc
import PyQt4.QtGui as qg
import stackbrowserQtUI as ui
import PointTable as pt
import StackPoints as sps
import tiffstack as ts
import Tkinter as Tk
import tkFileDialog


class MainWindow(qg.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        setter = ui.Ui_MainWindow()
        ui.Ui_MainWindow.setupUi(setter, self)
        action_open = setter.action_Open

        action_open.triggered.connect(lambda: self.action_handler('open'))

        self.stack = None
        self.z = None
        self.scale = 1.0
        self.image = None
        self.COLORTABLE = []
        for i in range(256):
            self.COLORTABLE.append(qg.qRgb(i / 4, i, i / 2))

        self.splitter = setter.splitter

        self.scene = qg.QGraphicsScene()
        self.view = _MyGraphicsView(setter.graphicsView)
        self.view.setMouseTracking(True)

        self.view.setScene(self.scene)
        self.view.fitInView(self.scene.sceneRect(), qc.Qt.KeepAspectRatio)

        self.view.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)

        self.view.keyPressEvent = self.keyPressEvent

        self.imageLabel = qg.QLabel()
        self.imageLabel.setSizePolicy(qg.QSizePolicy.Ignored, qg.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        # Note: palette not guaranteed to be cross-platform
        palette = qg.QPalette()
        palette.setColor(qg.QPalette.Background, qc.Qt.white)
        self.imageLabel.setPalette(palette)

        self.scene.addWidget(self.imageLabel)

        self.points = sps.DrawingPointsWidget(self)
        self.scene.addWidget(self.points)

        self.leftToolbar = setter.toolBar
        self.topToolbar = setter.toolBar_2

        self.zoomSpinBox = qg.QSpinBox()
        self.zoomSpinBox.setRange(1, 400)
        self.zoomSpinBox.setSuffix(" %")
        self.zoomSpinBox.setValue(100)
        self.zoomSpinBox.setToolTip("Zoom the image")
        self.zoomSpinBox.setStatusTip(self.zoomSpinBox.toolTip())
        self.zoomSpinBox.setFocusPolicy(qc.Qt.NoFocus)

        self.list = qg.QTableView(self)
        self.list.setFont(qg.QFont("Arial", 10))
        self.leftToolbar.addWidget(self.list)

    def action_handler(self, handle, *args):
        valid_funcs = {'open': self._open, 'pan': self._pan, 'zoom': self._zoom}

        valid_funcs[handle](args)

    def eventFilter(self, source, event):
        if event.type() == qc.QEvent.Wheel or event.type() == qc.QEvent.GraphicsSceneWheel:
            self.wheelEvent(event)

        if event.type() == qc.QEvent.MouseMove and source is self.view.viewport():
            pos = event.pos()
            print('mouse move: (%d, %d)' % (pos.x(), pos.y()))
            # self.updateStatus('mouse ' + str(pos.x()) + ' ' + str(pos.y()))

        if event.type() == qc.QEvent.KeyPress:
            # self.updateStatus('mouse ' + str(pos.x()) + ' ' + str(pos.y()))
            self.keyPressEvent(event)

        if event.type() == qc.QEvent.Resize:
            self.resizeEvent(event)

        return qg.QMainWindow.eventFilter(self, source, event)

    def showEvent(self, event):
        size = self.splitter.size()
        self.view.resize(size)
        self.imageLabel.resize(size)
        print(self.imageLabel.size())

    def resizeEvent(self, event):
        if self.stack is not None:
            a = self.stack.get_slice(self.z)
            self.image = qg.QImage(a.tostring(), a.shape[0], a.shape[1], qg.QImage.Format_Indexed8)
            self.image.setColorTable(self.COLORTABLE)
            p = qg.QPixmap.fromImage(self.image)
            self.view.resize(self.splitter.width(), self.splitter.width())
            self.imageLabel.resize(self.splitter.width(), self.splitter.width())
            self.imageLabel.setPixmap(p.scaled(self.imageLabel.width(), self.imageLabel.width()))
        else:
            self.view.resize(self.width(), self.width())
            self.imageLabel.resize(self.width(), self.width())

    def wheelEvent(self, event):
        if self.stack is not None:
            self.z -= np.sign(event.delta())
            if self.z < 0:
                self.z = 0
            if self.z > self.stack.maxz:
                self.z = self.stack.maxz
            # print 'MyWindow.wheelEvent()', event.delta(), self.z
            # self.label.setText("Total Steps: "+QString.number(self.x))

            a = self.stack.get_slice(self.z)
            self.image = qg.QImage(a.tostring(), a.shape[0], a.shape[1], qg.QImage.Format_Indexed8)
            self.image.setColorTable(self.COLORTABLE)
            self.imageLabel.setPixmap(qg.QPixmap.fromImage(self.image))
            self.update()

    def keyPressEvent(self, event):
        # print 'window.keyPressEvent:', event.text()
        # use QLabel.setGeometry(h,v,w,h) to pan the image
        # print 'keyPressEvent()'
        panvalue = 20
        zoomfactor = 1.5
        k = event.key()
        pan_keys = [qc.Qt.Key_Left, qc.Qt.Key_Right, qc.Qt.Key_Up, qc.Qt.Key_Down, qc.Qt.Key_Enter, qc.Qt.Key_Return]
        zoom_keys = [qc.Qt.Key_Plus, qc.Qt.Key_Minus, qc.Qt.Key_Enter, qc.Qt.Key_Return]
        if k in pan_keys:
            self.action_handler('pan', k, panvalue)
        if k in zoom_keys:
            self.action_handler('zoom', k, zoomfactor)

    def _open(self, args):
        root = Tk.Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        fpath = tkFileDialog.askopenfilename(
            initialdir=os.path.expanduser('~/Desktop'))
        self.stack = ts.TiffStack(fpath)

        self.z = 0
        a = self.stack.get_slice(0)
        self.image = qg.QImage(a.tostring(), a.shape[0], a.shape[1], qg.QImage.Format_Indexed8)
        self.image.setColorTable(self.COLORTABLE)
        p = qg.QPixmap.fromImage(self.image)
        self.imageLabel.setPixmap(p.scaled(self.imageLabel.width(), self.imageLabel.width()))
        pointModel = pt.PointTable(self.stack.node_db.dframe)
        self.list.setModel(pointModel)
        # self.view.fitInView(self.scene.sceneRect(), qc.Qt.KeepAspectRatio)

    def _pan(self, args):
        key = args[0]
        panvalue = args[1]
        if self.stack is not None:
            if key == qc.Qt.Key_Left:
                # self.imageX -= panvalue
                self.view.move(self.view.x() - panvalue, self.view.y())
            if key == qc.Qt.Key_Right:
                # self.imageX += panvalue
                self.view.move(self.view.x() + panvalue, self.view.y())
            if key == qc.Qt.Key_Up:
                # self.imageY -= panvalue
                self.view.move(self.view.x(), self.view.y() - panvalue)
            if key == qc.Qt.Key_Down:
                # self.imageY += panvalue
                self.view.move(self.view.x(), self.view.y() + panvalue)
            if key == qc.Qt.Key_Enter or key == qc.Qt.Key_Return:
                print 'reset image to full view and center'
                self.view.move(0, 0)

    def _zoom(self, args):
        key = args[0]
        factor = args[1]
        if key == qc.Qt.Key_Plus:
            self.scale *= factor
            self.view.setTransformationAnchor(qg.QGraphicsView.AnchorUnderMouse)
            self.view.scale(factor, factor)
        if key == qc.Qt.Key_Minus:
            self.scale /= factor
            self.view.setTransformationAnchor(qg.QGraphicsView.AnchorUnderMouse)
            self.view.scale(1.0/factor, 1.0/factor)
        if key == qc.Qt.Key_Enter or key == qc.Qt.Key_Return:
            self.view.setTransformationAnchor(qg.QGraphicsView.AnchorUnderMouse)
            self.view.scale(1.0/self.scale, 1.0/self.scale)
            self.scale = 1.0


class _MyGraphicsView(qg.QGraphicsView):
    """
    Empty abstract class; suppresses default QGraphicsView scroll behavior.
    """
    def scrollContentsBy(self, a, b):
        pass


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
