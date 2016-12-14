import PyQt4.QtCore as qc
import PyQt4.QtGui as qg


class DrawingPointsWidget(qg.QWidget):
    def __init__(self, browser):
        super(qg.QWidget, self).__init__()
        self.nodes = {}
        self.slabs = {}

        # Want to pass reference to keep z up-to-date
        self.browser = browser
        self.scaleFactor = 1  # fraction of total
        self.isVisible = 1

        self.setWindowFlags(self.windowFlags() | qc.Qt.FramelessWindowHint)
        self.setMouseTracking(True)

        self.setAttribute(qc.Qt.WA_TranslucentBackground)
        self.start_scale = None

    def setUI(self):

        self.setGeometry(0, 0, self.browser.splitter.width(), self.browser.splitter.width())
        # self.setWindowTitle('Points')
        self.show()

    def paintEvent(self, e):
        self.setUI()

    def initPoints(self, xfactor=None, yfactor=None, xtranslate=None, ytranslate=None):

        pen = qg.QPen(qc.Qt.cyan, 4, qc.Qt.SolidLine, qc.Qt.RoundCap)
        brush = qg.QBrush(qc.Qt.cyan)

        rectWidth = 7
        rectHeight = 7

        offset = 1

        # Note: Might break on zoom/further manipulations; more testing necessary
        self.start_scale = float(self.browser.splitter.width()) / self.browser.stack.imarray.shape[1]

        if xfactor is None:
            xfactor = self.start_scale
        else:
            xfactor *= self.start_scale

        if yfactor is None:
            yfactor = self.start_scale
        else:
            yfactor *= self.start_scale

        if xtranslate is None:
            xtranslate = 0

        if ytranslate is None:
            ytranslate = 0

        for slab in self.browser.stack.slab_db.dframe.itertuples():
            s = qg.QGraphicsEllipseItem(int(slab.x * xfactor / self.browser.stack.dx +
                                        xtranslate), int(slab.y * yfactor / self.browser.stack.dy +
                                        ytranslate), rectWidth, rectHeight)
            s.setPen(pen)
            s.setBrush(brush)
            s.hide()
            if slab.z not in self.slabs:
                self.slabs[slab.z] = [s]
            else:
                self.slabs[slab.z].append(s)
            self.browser.scene.addItem(s)
            # TODO: Draw edges

        pen.setColor(qc.Qt.red)
        pen.setWidth(7)
        brush.setColor(qc.Qt.red)

        for node in self.browser.stack.node_db.dframe.itertuples():
            n = qg.QGraphicsEllipseItem(int(node.x * xfactor / self.browser.stack.dx +
                                        xtranslate), int(node.y * yfactor / self.browser.stack.dy +
                                        ytranslate), rectWidth, rectHeight)
            n.setPen(pen)
            n.setBrush(brush)
            n.hide()
            if node.z not in self.nodes:
                self.nodes[node.z] = [n]
            else:
                self.nodes[node.z].append(n)
            self.browser.scene.addItem(n)

    def drawPoints(self, resize=False):

        if not self.isVisible:
            return

        offset = 1

        # Min slice
        d1 = int(self.browser.z - offset)
        prev = d1 - 1
        if d1 < 0:
            d1 = 0
            prev = None

        if prev:
            if prev in self.slabs:
                for s in self.slabs[prev]:
                    s.hide()

            if prev in self.nodes:
                for n in self.nodes[prev]:
                    n.hide()

        # Max slice
        d2 = int(self.browser.z + offset)
        nxt = d2 + 1
        if d2 > self.browser.stack.maxz:
            d2 = int(self.browser.stack.maxz)
            nxt = None

        if nxt:
            if nxt in self.slabs:
                for s in self.slabs[nxt]:
                    s.hide()

            if nxt in self.nodes:
                for n in self.nodes[nxt]:
                    n.hide()

        for z in range(d1, d2 + 1):
            if z in self.slabs:
                for s in self.slabs[z]:
                    if resize:
                        scale = float(self.browser.splitter.width()) / self.browser.stack.imarray.shape[1]
                        s.setPos(s.x() / self.start_scale * scale,
                                               s.y() / self.start_scale * scale)
                        s.update()
                    s.show()

            if z in self.nodes:
                for n in self.nodes[z]:
                    if resize:
                        n.resize()
                        n.update()
                    n.show()
