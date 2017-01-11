import PyQt4.QtCore as qc
import PyQt4.QtGui as qg


class DrawingPointsWidget(qg.QWidget):
    def __init__(self, browser):
        super(qg.QWidget, self).__init__()
        self.nodes = {}
        self.slabs = {}
        self.edge_segs = {}

        # Want to pass reference to keep z up-to-date
        self.browser = browser
        self.scaleFactor = 1  # fraction of total
        self.isVisible = 1

        self.setWindowFlags(self.windowFlags() | qc.Qt.FramelessWindowHint)
        self.setMouseTracking(True)

        self.setAttribute(qc.Qt.WA_TranslucentBackground)
        self.start_scale = None
        self.cur_scale = None

    def setUI(self):

        self.setGeometry(0, 0, self.browser.splitter.width(), self.browser.splitter.width())
        # self.setWindowTitle('Points')
        self.show()

    def paintEvent(self, e):
        self.setUI()

    def initPoints(self, xfactor=None, yfactor=None, xtranslate=None, ytranslate=None):

        slab_pen = qg.QPen(qc.Qt.cyan, 4, qc.Qt.SolidLine, qc.Qt.RoundCap)
        slab_brush = qg.QBrush(qc.Qt.cyan)

        node_edge_pen = qg.QPen(qc.Qt.red, 1, qc.Qt.SolidLine, qc.Qt.RoundCap)
        node_edge_brush = qg.QBrush(qc.Qt.red)

        rectWidth = 7
        rectHeight = 7

        # Note: Might break on zoom/further manipulations; more testing necessary
        self.start_scale = float(self.browser.splitter.width()) / self.browser.stack.imarray.shape[1]
        self.cur_scale = self.start_scale

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

        time = 0
        prev_slab = None
        prev_xpos = 0
        prev_ypos = 0
        for slab in self.browser.stack.slab_db.dframe.itertuples():
            s = self.Slab(0.0, 0.0, rectWidth, rectHeight, dfentry=slab)
            xpos = slab.x * xfactor / self.browser.stack.dx + xtranslate
            ypos = slab.y * yfactor / self.browser.stack.dy + ytranslate
            s.setPos(xpos, ypos)
            s.setPen(slab_pen)
            s.setBrush(slab_brush)
            s.hide()

            if slab.z not in self.slabs:
                self.slabs[slab.z] = [s]
            else:
                self.slabs[slab.z].append(s)
            self.browser.scene.addItem(s)

            if time == 0:
                prev_slab = s
                prev_xpos = xpos
                prev_ypos = ypos
                time += 1
            else:
                if slab.edgeIdx == prev_slab.dfentry.edgeIdx and (
                            slab.i == prev_slab.dfentry.i + 1):
                    # Connect
                    es = self.EdgeSegment(0.0, 0.0, 0.0, 0.0, idx=slab.edgeIdx)
                    es.endpoints = [prev_slab, s]
                    xpos = slab.x * xfactor / self.browser.stack.dx + xtranslate
                    ypos = slab.y * yfactor / self.browser.stack.dy + ytranslate
                    es.setLine(prev_xpos, prev_ypos, xpos, ypos)
                    es.setPen(node_edge_pen)
                    es.hide()
                    if slab.edgeIdx not in self.edge_segs:
                        self.edge_segs[slab.edgeIdx] = [es]
                    else:
                        self.edge_segs[slab.edgeIdx].append(es)
                    self.browser.scene.addItem(es)
                prev_slab = s
                prev_xpos = xpos
                prev_ypos = ypos
                time += 1

        node_edge_pen.setWidth(7)

        for node in self.browser.stack.node_db.dframe.itertuples():
            n = self.Node(0.0, 0.0, rectWidth, rectHeight, dfentry=node)
            n.setPos(node.x * xfactor / self.browser.stack.dx +
                     xtranslate, node.y * yfactor / self.browser.stack.dy +
                     ytranslate)
            n.setPen(node_edge_pen)
            n.setBrush(node_edge_brush)
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

        if prev is not None:
            if prev in self.slabs:
                for s in self.slabs[prev]:
                    s.hide()
                    if s.dfentry.edgeIdx in self.edge_segs:
                        for es in self.edge_segs[s.dfentry.edgeIdx]:
                            if es.endpoints[0].dfentry.z <= prev and es.endpoints[1].dfentry.z <= prev:
                                es.hide()

            if prev in self.nodes:
                for n in self.nodes[prev]:
                    n.hide()

        # Max slice
        d2 = int(self.browser.z + offset)
        nxt = d2 + 1
        if d2 > self.browser.stack.maxz:
            d2 = int(self.browser.stack.maxz)
            nxt = None

        if nxt is not None:
            if nxt in self.slabs:
                for s in self.slabs[nxt]:
                    s.hide()
                    if s.dfentry.edgeIdx in self.edge_segs:
                        for es in self.edge_segs[s.dfentry.edgeIdx]:
                            if es.endpoints[0].dfentry.z >= nxt and es.endpoints[1].dfentry.z >= nxt:
                                es.hide()

            if nxt in self.nodes:
                for n in self.nodes[nxt]:
                    n.hide()

        scale = float(self.browser.splitter.width()) / self.browser.stack.imarray.shape[1]
        if resize:
            for k in self.slabs:
                for s in self.slabs[k]:
                    s.setPos(s.pos() / self.cur_scale * scale)
            for idx in self.edge_segs:
                # Handle error case of edge with one slab
                try:
                    for es in self.edge_segs[idx]:
                        temp = es.line()
                        temp.setPoints(es.line().p1() / self.cur_scale * scale,
                                       es.line().p2() / self.cur_scale * scale)
                        es.setLine(temp)
                except KeyError:
                    pass
            for k in self.nodes:
                for n in self.nodes[k]:
                    n.setPos(n.pos() / self.cur_scale * scale)

        for z in range(d1, d2 + 1):
            visible_edges = []
            if z in self.slabs:
                for s in self.slabs[z]:
                    s.show()
                    if s.dfentry.edgeIdx not in visible_edges:
                        visible_edges.append(s.dfentry.edgeIdx)
                for idx in visible_edges:
                    for es in self.edge_segs[idx]:
                        if es.endpoints[0].isVisible() or es.endpoints[1].isVisible():
                            es.show()

            if z in self.nodes:
                for n in self.nodes[z]:
                    n.show()

        self.cur_scale = scale

    class Node(qg.QGraphicsEllipseItem):
        def __init__(self, *_args, **kwargs):
            super(qg.QGraphicsEllipseItem, self).__init__(*_args)
            self.dfentry = None
            if 'dfentry' in kwargs:
                self.dfentry = kwargs['dfentry']

    class Slab(qg.QGraphicsEllipseItem):
        def __init__(self, *_args, **kwargs):
            super(qg.QGraphicsEllipseItem, self).__init__(*_args)

            self.dfentry = None
            if 'dfentry' in kwargs:
                self.dfentry = kwargs['dfentry']

    class EdgeSegment(qg.QGraphicsLineItem):
        def __init__(self, *_args, **kwargs):
            super(qg.QGraphicsLineItem, self).__init__(*_args)
            self.idx = None
            if 'idx' in kwargs:
                self.idx = kwargs['idx']
            self.endpoints = []
