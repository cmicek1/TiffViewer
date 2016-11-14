import PyQt4.QtCore as qc
import PyQt4.QtGui as qg


class DrawingPointsWidget(qg.QWidget):
    def __init__(self, browser):
        super(qg.QWidget, self).__init__(browser)

        # Want to pass reference to keep z up-to-date
        self.scaleFactor = 1  # fraction of total
        self.isVisible = 1

        self.setWindowFlags(self.windowFlags() | qc.Qt.FramelessWindowHint)

        # self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(qc.Qt.WA_TranslucentBackground)
        # self.setAttribute(Qt.WA_PaintOnScreen)

        # self.setAttribute(Qt.WA_TransparentForMouseEvents);

        self.setUI()

    def setUI(self):

        self.setGeometry(0, 0, self.parent().imageLabel.width(), self.parent().imageLabel.height())
        # self.setWindowTitle('Points')
        self.show()

    def paintEvent(self, e):
        qp = qg.QPainter(self)
        if self.parent().stack is not None:
            self.drawPoints(qp)

    def drawPoints(self, qp):
        # print 'DrawingPointsWidget::drawPoints()'

        if not self.isVisible:
            return

        qp.setPen(qg.QPen(qc.Qt.red, 12, qc.Qt.DashDotLine, qc.Qt.RoundCap))

        rectWidth = 7
        rectHeight = 7

        # TODO: Rewrite for current stack class
        xyz = self.parent().stack.nodedb.dframe.getMask(self.parent().z)
        xyz /= float(self.map.stackList[1].header['voxelx'])
        xyz *= self.scaleFactor
        # xyz = abs(np.random.random((20,20)) * 100)
        num = len(xyz)
        for i in range(num):
            x = xyz[i][0]
            y = xyz[i][1]
            qp.drawEllipse(x, y, rectWidth, rectHeight)