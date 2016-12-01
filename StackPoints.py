import PyQt4.QtCore as qc
import PyQt4.QtGui as qg


class DrawingPointsWidget(qg.QWidget):
    def __init__(self, browser):
        super(qg.QWidget, self).__init__()

        # Want to pass reference to keep z up-to-date
        self.browser = browser
        self.scaleFactor = 1  # fraction of total
        self.isVisible = 1

        self.setWindowFlags(self.windowFlags() | qc.Qt.FramelessWindowHint)
        self.setMouseTracking(True)

        # self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(qc.Qt.WA_TranslucentBackground)
        # self.setAttribute(Qt.WA_PaintOnScreen)

        # self.setAttribute(Qt.WA_TransparentForMouseEvents);

    def setUI(self):

        self.setGeometry(0, 0, self.browser.splitter.width(), self.browser.splitter.width())
        # self.setWindowTitle('Points')
        self.show()

    def paintEvent(self, e):
        self.setUI()
        qp = qg.QPainter(self)
        if self.browser.stack is not None:
            self.drawPoints(qp)

    def drawPoints(self, qp, xfactor=None, yfactor=None, xtranslate=None, ytranslate=None):
        # print 'DrawingPointsWidget::drawPoints()'

        if not self.isVisible:
            return

        qp.setPen(qg.QPen(qc.Qt.red, 6, qc.Qt.DashDotLine, qc.Qt.RoundCap))

        rectWidth = 7
        rectHeight = 7

        offset = 1

        # Note: Might break on zoom/further manipulations; more testing necessary
        start_scale = float(self.browser.splitter.width()) / self.browser.stack.imarray.shape[1]

        if xfactor is None:
            xfactor = start_scale
        else:
            xfactor *= start_scale

        if yfactor is None:
            yfactor = start_scale
        else:
            yfactor *= start_scale

        if xtranslate is None:
            xtranslate = 0

        if ytranslate is None:
            ytranslate = 0

        # Min slice
        d1 = int(self.browser.z - offset)
        if d1 < 0:
            d1 = 0

        # Max slice
        d2 = int(self.browser.z + offset)
        if d2 > self.browser.stack.maxz:
            d2 = int(self.browser.stack.maxz)
        nodes = self.browser.stack.node_db.dframe.loc[(d1 <= self.browser.stack.node_db.dframe['z']) &
                                                       (self.browser.stack.node_db.dframe['z'] <= d2)]
        for node in nodes.itertuples():
            # TODO: Replace these with QGraphicsItems, add to scene
            qp.drawEllipse(int(node.x * xfactor / self.browser.stack.dx +
                           xtranslate), int(node.y * yfactor / self.browser.stack.dy +
                           ytranslate), rectWidth, rectHeight)
