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
    """
    Main application window for Qt Stack Browser. Subclasses QMainWindow, and serves as the top-level user interface
    for the application. It handles widget layout, file I/O, display, and user input.
    """
    def __init__(self):
        """
        Initializer for the Main Window. First calls QMainWindow initializer, then creates layout and UI with help
        from the Ui_MainWindow class in stackbrowserQtUI.py, exported from Qt Designer.
        """
        super(qg.QMainWindow, self).__init__()  # Default initializer for QMainWindow called first
        setter = ui.Ui_MainWindow()  # Tool for setting UI
        ui.Ui_MainWindow.setupUi(setter, self)
        action_open = setter.action_Open

        action_open.triggered.connect(lambda: self.action_handler('open'))

        # Add additional relevant attributes
        self.stack = None
        self.z = None
        self.scale = 1.0
        self.image = None
        self.COLORTABLE = []
        # Set default color table for 8-bit images
        for i in range(256):
            self.COLORTABLE.append(qg.qRgb(i / 4, i, i / 2))

        self.splitter = setter.splitter

        # Initialize the scene and the view of the application, the two most-often used attributes
        self.scene = qg.QGraphicsScene()
        self.view = _MyGraphicsView(setter.graphicsView)  # Uses hidden class derived from QGraphicsView to suppress
                                                          # default scrolling behavior

        self.view.setScene(self.scene)
        self.view.fitInView(self.scene.sceneRect(), qc.Qt.KeepAspectRatio)

        self.view.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)

        self.view.keyPressEvent = self.keyPressEvent  # Pass top-level keyboard events to view

        # Create container for the image to be displayed (easy with a QLabel)
        self.imageLabel = qg.QLabel()
        self.imageLabel.setSizePolicy(qg.QSizePolicy.Ignored, qg.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        # Note: palette not guaranteed to be cross-platform
        palette = qg.QPalette()
        palette.setColor(qg.QPalette.Background, qc.Qt.white)
        self.imageLabel.setPalette(palette)

        self.scene.addWidget(self.imageLabel)

        # Add custom widget handling display of and interaction with any items overlaying the image
        self.points = sps.DrawingPointsWidget(self)
        self.scene.addWidget(self.points)

        # Add removable toolbars for useful interaction and information display
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
        self.list.setSelectionBehavior(qg.QAbstractItemView.SelectRows)
        # TODO: Remove selection on second click
        self.leftToolbar.addWidget(self.list)

    def action_handler(self, handle, *args):
        """
        Custom universal handler for valid hidden functions. Uses a dictionary associating keywords with their
        respective functions, and passes along necessary arguments for execution. Useful for both utility functions
        and Qt signals and slots.

        :param handle: Keyword for the desired function
        :param args: Arguments to be passed to the function named by 'handle' (the function must accept *args as a
                     parameter, even if it is unused

        :type handle: str
        :type args: list

        :return: None
        """
        valid_funcs = {'open': self._open, 'pan': self._pan, 'zoom': self._zoom, '_node_select': self._node_select}

        valid_funcs[handle](*args)

    def eventFilter(self, watched, event):
        """
        Overloaded method from QMainWindow. Catches the event from watched and allows it to proceed if it is of the
        appropriate type.

        :param watched: The source (widget) of the caught event
        :param event: The event that was caught

        :type watched: PyQt4.QtCore.QObject
        :type event: PyQt4.QtCore.QEvent

        :return: True if 'event' was filtered out, False else
        :rtype: bool
        """
        # TODO: Detect when toolbar is moved, and reposition points appropriately
        if event.type() == qc.QEvent.Wheel or event.type() == qc.QEvent.GraphicsSceneWheel:
            self.wheelEvent(event)

        if event.type() == qc.QEvent.MouseMove and watched is self.view.viewport():
            pos = event.pos()
            print('mouse move: (%d, %d)' % (pos.x(), pos.y()))
            # self.updateStatus('mouse ' + str(pos.x()) + ' ' + str(pos.y()))

        if event.type() == qc.QEvent.KeyPress:
            # self.updateStatus('mouse ' + str(pos.x()) + ' ' + str(pos.y()))
            self.keyPressEvent(event)

        if event.type() == qc.QEvent.Resize:
            self.resizeEvent(event)

        # After taking custom action, send back to superclass event filter for default behavior
        return qg.QMainWindow.eventFilter(self, watched, event)

    def showEvent(self, event):
        """
        Overloaded method from QMainWindow. Handles QShowEvents, which occur when the application window is shown on
        the screen.

        :param event: The QShowEvent received

        :type event: PyQt4.QtGui.QShowEvent

        :return: None
        """

        # Simply resizes widgets contained in the application to be of the appropriate size when the window is first
        # shown.
        size = self.splitter.size()
        self.view.resize(size)
        self.imageLabel.resize(size)
        print(self.imageLabel.size())

    def resizeEvent(self, event):
        """
        Overloaded method from QMainWindow. Handles QResizeEvents when the window is resized.

        :param event: The QResizeEvent received

        :type event: PyQt4.QtGui.QResizeEvent

        :return: None
        """
        if self.stack is not None:
            # Resize image and overlay to new size
            # Add drawing nodes to window display functions
            a = self.stack.get_slice(self.z)
            self.image = qg.QImage(a.tostring(), a.shape[0], a.shape[1], qg.QImage.Format_Indexed8)
            self.image.setColorTable(self.COLORTABLE)
            p = qg.QPixmap.fromImage(self.image)
            self.view.resize(self.splitter.width(), self.splitter.width())
            self.imageLabel.resize(self.splitter.width(), self.splitter.width())
            self.imageLabel.setPixmap(p.scaled(self.imageLabel.width(), self.imageLabel.width()))

            # Now draw new nodes
            self.points.drawPoints(resize=True)
        else:
            # Resize container widgets to new window size
            self.view.resize(self.width(), self.width())
            self.imageLabel.resize(self.width(), self.width())

    def wheelEvent(self, event):
        """
        Overloaded method from QMainWindow. Handles QWheelEvents when the mouse wheel is scrolled and the resulting
        event is accepted.

        :param event: The accepted QWheelEvent

        :type event: PyQt4.QtGui.QWheelEvent

        :return: None
        """
        # If stack is loaded, view next slice in scroll direction within the valid range.
        if self.stack is not None:
            # Add drawing nodes to window display functions
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
            # Now draw new nodes
            self.points.drawPoints()

    def keyPressEvent(self, event):
        """
        Overloaded method from QMainWindow. Handles QKeyEvents when a key is pressed and the resulting event is
        accepted.

        :param event: The accepted QKeyEvent

        :type event: PyQt4.QtGui.QKeyEvent

        :return: None
                """

        # Values for amount of pixels to pan by (wrt original image size) and factor to zoom by. Hard coded for now,
        # but the plan is to have these as tunable options later, if desired.
        panvalue = 20
        zoomfactor = 1.5
        k = event.key()
        pan_keys = [qc.Qt.Key_Left, qc.Qt.Key_Right, qc.Qt.Key_Up, qc.Qt.Key_Down, qc.Qt.Key_Enter, qc.Qt.Key_Return]
        zoom_keys = [qc.Qt.Key_Plus, qc.Qt.Key_Minus, qc.Qt.Key_Enter, qc.Qt.Key_Return]
        if k in pan_keys:
            self.action_handler('pan', k, panvalue)
        if k in zoom_keys:
            self.action_handler('zoom', k, zoomfactor)

    def _node_select(self, *args):
        if len(args) == 1:
            node = args[0]
            cur_model = self.list.model()
            self.list.selectionModel().select(cur_model.index(node.dfentry.i, 0),
                                              qg.QItemSelectionModel.Select | qg.QItemSelectionModel.Rows)

        if len(args) == 2:
            selected = args[0]
            deselected = args[1]

            prev_row = None
            for node in selected.indexes():
                if node.row() != prev_row:
                    prev_row = node.row()
                    n = self.points.nodes_by_idx[node.row()]
                    n.show()
                    if not n.isSelected():
                        n.setSelected(True)

            prev_row = None
            for node in deselected.indexes():
                if node.row() != prev_row:
                    prev_row = node.row()
                    n = self.points.nodes_by_idx[node.row()]
                    if n.isSelected():
                        n.setSelected(False)

    def _open(self, *args):
        """
        Hidden function invoked by the action handler that opens and displays a TiffStack. Called by pressing 'Open'
        in the 'File' menu of the GUI.

        :param args: Unused, but required in the function signature for it to be handled correctly by the action
                     handler.

        :type args: None

        :return: None
        """
        # Open a dialog box allowing the user to select a TiffStack to display. See tiffstack.py and the repository
        # README for more info.
        root = Tk.Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        fpath = tkFileDialog.askopenfilename(
            initialdir=os.path.expanduser('~/Desktop'))
        self.stack = ts.TiffStack(fpath)

        # Start at slice 0
        self.z = 0
        a = self.stack.get_slice(0)
        self.image = qg.QImage(a.tostring(), a.shape[0], a.shape[1], qg.QImage.Format_Indexed8)
        self.image.setColorTable(self.COLORTABLE)
        p = qg.QPixmap.fromImage(self.image)
        self.imageLabel.setPixmap(p.scaled(self.imageLabel.width(), self.imageLabel.width()))
        old = self.list.selectionModel()
        pointModel = pt.PointTable(self.stack.node_db.dframe)
        self.list.setModel(pointModel)
        self.list.selectionModel().selectionChanged.connect(lambda selected, deselected, func=self.action_handler: func(
            '_node_select', selected, deselected))
        del old

        # Create initial overlay and internal representation of graph data
        self.points.initPoints()
        self.points.drawPoints()

    def _pan(self, *args):
        """
        Hidden function invoked by the action handler that pans the current view of the open TiffStack. Called by
        pressing any of the arrow keys; the view will pan in the respective direction. Also moves the view back to
        center when the Enter or Return keys are pressed.

        :param args: First argument is the key from the QKeyEvent caught by 'keyPressEvent'; second is the
                     number of pixels to pan by wrt the initial size of the image

        :type args: list[int, int]

        :return: None
        """
        key = args[0]
        panvalue = args[1]
        if self.stack is not None:
            if key == qc.Qt.Key_Left:
                self.view.move(self.view.x() - panvalue, self.view.y())
            if key == qc.Qt.Key_Right:
                self.view.move(self.view.x() + panvalue, self.view.y())
            if key == qc.Qt.Key_Up:
                self.view.move(self.view.x(), self.view.y() - panvalue)
            if key == qc.Qt.Key_Down:
                self.view.move(self.view.x(), self.view.y() + panvalue)
            if key == qc.Qt.Key_Enter or key == qc.Qt.Key_Return:
                print('reset image to full view and center')
                self.view.move(0, 0)

    def _zoom(self, *args):
        """
        Hidden function invoked by the action handler that zooms the current view of the open TiffStack with respect
        to the current mouse position, or returns the view to its initial size. Called by pressing the plus, minus, and
        Enter/Return keys to zoom in, out, and to the initial scale, respectively.

        :param args: First argument is the key from the QKeyEvent caught by 'keyPressEvent'; second is the
                     percentage of the current view size to zoom by

        :type args: list[int, float]

        :return: None
        """
        key = args[0]
        factor = args[1]
        # Qt's default implementation of transformations with respect to the mouse position only works correctly if
        # the view is not a derived class with the scroll disabled, so the code below is a bit of a hacky workaround.
        # It maps the global position of the mouse to scene coordinates, scales the view appropriately, then finds
        # the scene coordinates of the new mouse position and translates the view so the old and new positions are
        # coincident.
        old_pos = self.view.mapToScene(self.view.mapFromGlobal(qg.QCursor.pos()))
        if key == qc.Qt.Key_Plus:  # Zoom in
            self.scale *= factor
            self.view.scale(factor, factor)
            new_pos = self.view.mapToScene(self.view.mapFromGlobal(qg.QCursor.pos()))
            delta = new_pos - old_pos
            self.view.translate(delta.x(), delta.y())
        # TODO: Fix incorrect view size when zooming out
        if key == qc.Qt.Key_Minus:  # Zoom out
            self.scale /= factor
            self.view.scale(1.0/factor, 1.0/factor)
            new_pos = self.view.mapToScene(self.view.mapFromGlobal(qg.QCursor.pos()))
            delta = new_pos - old_pos
            self.view.translate(delta.x(), delta.y())
        if key == qc.Qt.Key_Enter or key == qc.Qt.Key_Return:  # Return to initial size
            self.view.scale(1.0/self.scale, 1.0/self.scale)
            new_pos = self.view.mapFromScene(0, 0)
            delta = -new_pos
            self.view.translate(delta.x(), delta.y())
            self.scale = 1.0


class _MyGraphicsView(qg.QGraphicsView):
    """
    Empty abstract class; suppresses default QGraphicsView scroll behavior.
    """
    def __init__(self, uiview):
        """
        Initializer for the derived class; initializes the QGraphicsView from the UI setter using the default
        initializer of QGraphicsView

        :param uiview: QGraphicsView to initialize; should be from UI made with Qt Designer

        :type uiview: PyQt4.QtGui.QGraphicsView
        """
        super(qg.QGraphicsView, self).__init__(uiview)

    def scrollContentsBy(self, dx, dy):
        """
        Overloaded method of QAbstractScroll area, of which QGraphicsView is derived. Determines how much the current
        view should scroll when its scroll bars are moved by dx and dy. This implementation does nothing because
        the scrolling behavior of a QGraphicsView enabled by default conflicts with the intuitive scrolling by z slice
        of the application.

        :param dx: Number of pixels in the x direction the scroll bars have moved
        :param dy: Number of pixels in the y direction the scroll bars have moved

        :type dx: int
        :type dy: int

        :return: None
        """
        # Apparently this affects the transformation anchor
        pass


def _exit_handler():
    """
    Signal connected to the top-level application class (QApplication) to terminate the program correctly in Python,
    as PyQt4 handles Python garbage collection incorrectly.

    :return: None
    """
    sys.exit(0)


def main():

    app = qg.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.aboutToQuit.connect(_exit_handler)
    return app.exec_()


if __name__ == '__main__':
    main()
