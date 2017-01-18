import PyQt4.QtCore as qc
import PyQt4.QtGui as qg


class DrawingPointsWidget(qg.QWidget):
    """
    Custom QWidget class to regulate display of and user interaction with any overlays for the Stack
    Browser's TiffStack, as defined in the text files within its home directory. The objects it regulates are custom
    QGraphicsItems, defined below this class.
    """
    def __init__(self, browser):
        """
        Initializer for the QWidget. Calls the initializer of the superclass first, then initializes custom
        attributes. These include, among others:
            * nodes, a dictionary of Node lists organized by z slice: dict[int z, list[Node n]]
            * slabs, a dictionary of Slab lists organized by z slice: dict[int z, list[Slab s]]
            * edge_segs, a dictionary of EdgeSegments organized by edge index: dict[int edgeIdx, list[EdgeSegment es]]

        :param browser: The stack browser instance this widget will be a member of; passed so that all attributes are
                        passed by reference between both, and are up-to-date.

        :type browser: MainWindow
        """
        super(qg.QWidget, self).__init__()
        self.nodes = {}
        self.slabs = {}
        self.edge_segs = {}
        self.edges = {}

        # Want to pass reference to keep z up-to-date
        self.browser = browser
        self.scaleFactor = 1  # fraction of total
        self.isVisible = 1  # Show all points and edges by default

        self.setWindowFlags(self.windowFlags() | qc.Qt.FramelessWindowHint)
        self.setMouseTracking(True)

        self.setAttribute(qc.Qt.WA_TranslucentBackground)
        self.start_scale = None
        self.cur_scale = None

    def setUI(self):
        """
        Sets the widget to the appropriate size and triggers a display update to reflect the current state of all items.

        :return: None
        """

        self.setGeometry(0, 0, self.browser.splitter.width(), self.browser.splitter.width())
        self.show()

    def paintEvent(self, event):
        """
        Overloaded function from QWidget. Receives QPaintEvents for the widget and calls 'setUI' to display all items
        correctly.

        :param event: The QPaintEvent received

        :type event: PyQt4.QtGui.QPaintEvent

        :return: None
        """
        self.setUI()

    def initPoints(self, xfactor=None, yfactor=None, xtranslate=None, ytranslate=None):
        """
        Initializes all of this widget's derived QGraphicsItems to their initial state, placing them all in their
        correct positions based on the browser TiffStack's DataFrame members. All items are hidden from view until
        the current z slice is within a specified distance of the z-coordinate of each.

        :param xfactor: Scale factor for item x-coordinates (the previous scale by default)
        :param yfactor: Scale factor for item y-coordinates (the previous scale by default)
        :param xtranslate: Amount of pixels to translate each item in the x-direction (0 by default)
        :param ytranslate: Amount of pixels to translate each item in the y-direction (0 by default)

        :type xfactor: float
        :type yfactor: float
        :type xtranslate: int
        :type ytranslate: int

        :return: None
        """

        # Create pens and brushes to color nodes, slabs, and edges
        slab_pen = qg.QPen(qc.Qt.cyan, 4, qc.Qt.SolidLine, qc.Qt.RoundCap)
        slab_brush = qg.QBrush(qc.Qt.cyan)

        node_edge_pen = qg.QPen(qc.Qt.red, 1, qc.Qt.SolidLine, qc.Qt.RoundCap)
        node_edge_brush = qg.QBrush(qc.Qt.red)

        # Size of each node/slab's bounding box
        rectWidth = 7
        rectHeight = 7

        # Current scale of all items, determined by the size of the image container relative to the image
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

        # Place all items in the correct position, and store them in dicts
        time = 0
        prev_slab = None
        prev_xpos = 0
        prev_ypos = 0
        for slab in self.browser.stack.slab_db.dframe.itertuples():
            s = self.Slab(0.0, 0.0, rectWidth, rectHeight, dfentry=slab, widget=self)
            xpos = slab.x * xfactor / self.browser.stack.dx + xtranslate
            ypos = slab.y * yfactor / self.browser.stack.dy + ytranslate
            s.setPos(xpos - rectWidth/2, ypos - rectHeight/2)  # Note: Coordinates for QGraphicsEllipseItems are the
            # upper-left corner of the item's bounding box,
            # so need to translate to center
            s.setPen(slab_pen)
            s.setBrush(slab_brush)
            s.setZValue(s.zValue() + 1)
            s.hide()

            if slab.z not in self.slabs:
                self.slabs[slab.z] = [s]
            else:
                self.slabs[slab.z].append(s)
            self.browser.scene.addItem(s)

            # Connect each Slab that has a neighbor of the same edge index with an EdgeSegment
            if time == 0:
                prev_slab = s
                prev_xpos = xpos
                prev_ypos = ypos
                time += 1
            else:
                if slab.edgeIdx == prev_slab.dfentry.edgeIdx and (
                            slab.i == prev_slab.dfentry.i + 1):
                    # Connect
                    es = self.EdgeSegment(0.0, 0.0, 0.0, 0.0, idx=slab.edgeIdx, widget=self)
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

        for edge in self.browser.stack.edge_db.dframe.itertuples():
            idx = edge.i
            try:
                e = self.Edge(widget=self, idx=idx, dfentry=edge, edge_segs=self.edge_segs[idx])
                for seg in e.edge_segs:
                    for ep in seg.endpoints:
                        if ep not in e.slabs:
                            e.slabs.append(ep)
                self.edges[idx] = e
            except KeyError:
                pass

        # Change pen to Node specs
        node_edge_pen.setWidth(7)

        for node in self.browser.stack.node_db.dframe.itertuples():
            n = self.Node(0.0, 0.0, rectWidth, rectHeight, dfentry=node, widget=self)
            xpos = node.x * xfactor / self.browser.stack.dx + xtranslate
            ypos = node.y * yfactor / self.browser.stack.dy + ytranslate
            n.setPos(xpos - rectWidth/2, ypos - rectHeight/2)
            n.setPen(node_edge_pen)
            n.setBrush(node_edge_brush)
            n.setZValue(n.zValue() + 1)
            n.hide()
            if node.z not in self.nodes:
                self.nodes[node.z] = [n]
            else:
                self.nodes[node.z].append(n)
            self.browser.scene.addItem(n)

    def drawPoints(self, resize=False):
        """
        Function to determine which items to show in the current browser view. Checks for Nodes and Slabs in the
        current z slice +/- an offset value (1 slice by default), and EdgeSegments that have any visible endpoints,
        and displays them. Also rescales all items if the window is resized.

        :param resize: A boolean indicating if the call for this function occurred during a resize event.

        :type resize: bool

        :return: None
        """

        # If overlay is not visible, do nothing
        if not self.isVisible:
            return

        # Else, set offset from current z to search for items to be shown
        offset = 1

        # Calculate min slice in range
        d1 = int(self.browser.z - offset)
        prev = d1 - 1
        if d1 < 0:
            d1 = 0
            prev = None

        # If scrolling down, hide items in previous uppermost visible slice
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

        # Calculate max slice of range
        d2 = int(self.browser.z + offset)
        nxt = d2 + 1
        if d2 > self.browser.stack.maxz:
            d2 = int(self.browser.stack.maxz)
            nxt = None

        # If scrolling up, hide items in previous lowermost visible slice
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

        # Check scale out of scope so the current stored scale can be modified
        scale = float(self.browser.splitter.width()) / self.browser.stack.imarray.shape[1]
        if resize:  # Scale all items (both visible and invisible) via a linear iteration through each member dict,
            # so scales of all items are easy to keep track of
            for k in self.slabs:
                for s in self.slabs[k]:
                    s.setPos(s.pos() / self.cur_scale * scale)
            for idx in self.edge_segs:
                # Handle error case of edge with one slab (shouldn't occur, but can if there was an error in the
                # creation of the initial text file)
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
                    try:
                        for es in self.edge_segs[idx]:
                            if es.endpoints[0].isVisible() or es.endpoints[1].isVisible():
                                es.show()
                    except KeyError:
                        pass

            if z in self.nodes:
                for n in self.nodes[z]:
                    n.show()

        self.cur_scale = scale

    # TODO: Keep selection when scrolling
    class Node(qg.QGraphicsEllipseItem):
        """
        Class for nodes in the scene derived from QGraphicsEllipseItem. Useful for event handling and linking each
        item to its corresponding DataFrame entry.
        """
        def __init__(self, *_args, **kwargs):
            """
            Initializer for Node class. Uses _args to call initializer of superclass (QGraphicsEllipseItem),
            and accepts the keyword argument 'dfentry', which is the Node's corresponding DataFrame entry.

            :param _args: Default positional arguments for the QGraphicsEllipseItem initializer (unmodified)
            :param kwargs: Accepted keyword arguments (currently 'dfentry', which is assigned to the instance's
                           'dfentry' attribute).

            :type _args: list
            :type kwargs: dict[str, pandas.DataFrame]
            """
            super(qg.QGraphicsEllipseItem, self).__init__(*_args)
            self.setFlag(qg.QGraphicsItem.ItemIsSelectable)
            self.dfentry = None
            if 'dfentry' in kwargs:
                self.dfentry = kwargs['dfentry']
            if 'widget' in kwargs:
                self.widget = kwargs['widget']

        def paint(self, painter, option, widget=0):
            """
            Overloaded function from QGraphicsItem; determines how the item should be painted onto the screen.

            :param painter: A QPainter object, which manages low-level painting functions and includes a QPen and
                            QBrush for managing color, fill, and line style, among others.
            :param option: A QStyleOptionGraphicsItem instance Qt uses to store the options used when drawing the item.
            :param widget: The QWidget to paint on

            :type painter: PyQt4.QtGui.QPainter
            :type option: PyQt4.QtGui.QStyleOptionGraphicsItem
            :type widget: PyQt4.QtGui.QWidget

            :return: None
            """
            # Remove default Qt selection behavior
            tempop = option
            tempop.state &= not qg.QStyle.State_Selected
            qg.QGraphicsEllipseItem.paint(self, painter, tempop, widget)

        def itemChange(self, change, value):
            if change == qg.QGraphicsItem.ItemSelectedChange:
                # Note: Need to use '==' operator for condition to evaluate correctly. (Qt will cast the QVariant
                # 'value' to a boolean when evaluating only if the boolean equivalent operator is used.)
                if value == 1:
                    self.setBrush(qc.Qt.yellow)
                    self.setPen(qg.QPen(qc.Qt.yellow, 7, qc.Qt.SolidLine, qc.Qt.RoundCap))
                else:
                    self.setBrush(qc.Qt.red)
                    self.setPen(qg.QPen(qc.Qt.red, 7, qc.Qt.SolidLine, qc.Qt.RoundCap))
            return qg.QGraphicsEllipseItem.itemChange(self, change, value)

    class Slab(qg.QGraphicsEllipseItem):
        """
        Class for slabs in the scene derived from QGraphicsEllipseItem. Useful for event handling and linking each
        item to its corresponding DataFrame entry.
        """
        def __init__(self, *_args, **kwargs):
            """
            Initializer for Slab class. Uses _args to call initializer of superclass (QGraphicsEllipseItem),
            and accepts the keyword argument 'dfentry', which is the Slab's corresponding DataFrame entry.

            :param _args: Default positional arguments for the QGraphicsEllipseItem initializer (unmodified)
            :param kwargs: Accepted keyword arguments (currently 'dfentry', which is assigned to the instance's
                           'dfentry' attribute).

            :type _args: list
            :type kwargs: dict[str, pandas.DataFrame]
            """
            super(qg.QGraphicsEllipseItem, self).__init__(*_args)
            self.setFlag(qg.QGraphicsItem.ItemIsSelectable)
            self.dfentry = None
            if 'dfentry' in kwargs:
                self.dfentry = kwargs['dfentry']
            if 'widget' in kwargs:
                self.widget = kwargs['widget']

        def paint(self, painter, option, widget=0):
            """
            Overloaded function from QGraphicsItem; determines how the item should be painted onto the screen.

            :param painter: A QPainter object, which manages low-level painting functions and includes a QPen and
                            QBrush for managing color, fill, and line style, among others.
            :param option: A QStyleOptionGraphicsItem instance Qt uses to store the options used when drawing the item.
            :param widget: The QWidget to paint on

            :type painter: PyQt4.QtGui.QPainter
            :type option: PyQt4.QtGui.QStyleOptionGraphicsItem
            :type widget: PyQt4.QtGui.QWidget

            :return: None
            """
            # Remove default Qt selection behavior
            tempop = option
            tempop.state &= not qg.QStyle.State_Selected
            qg.QGraphicsEllipseItem.paint(self, painter, tempop, widget)

        def itemChange(self, change, value):
            if change == qg.QGraphicsItem.ItemSelectedChange:
                # Note: Need to use '==' operator for condition to evaluate correctly. (Qt will cast the QVariant
                # 'value' to a boolean when evaluating only if the boolean 'is equivalent' operator is used.)
                if value == 1:
                    self.widget.edges[self.dfentry.edgeIdx].setSelect(True)
                else:
                    self.widget.edges[self.dfentry.edgeIdx].setSelect(False)
            return qg.QGraphicsEllipseItem.itemChange(self, change, value)

    class EdgeSegment(qg.QGraphicsLineItem):
        """
        Class for edge segments in the scene derived from QGraphics:LineItem. Holds each segment's edge index and its
        two Slab endpoints.
        """
        def __init__(self, *_args, **kwargs):
            """
            Initializer for EdgeSegment class. Uses _args to call initializer of superclass (QGraphicsLineItem),
            and accepts the keyword argument 'idx', representing its edge index.

            :param _args: Default positional arguments for the QGraphicsEllipseItem initializer (unmodified)
            :param kwargs: Accepted keyword arguments (currently 'idx', which is assigned to the instance's
                           'idx' attribute).

            :type _args: list
            :type kwargs: dict[str, int]
            """
            super(qg.QGraphicsLineItem, self).__init__(*_args)
            self.setFlag(qg.QGraphicsItem.ItemIsSelectable)
            self.idx = None
            if 'idx' in kwargs:
                self.idx = kwargs['idx']
            if 'widget' in kwargs:
                self.widget = kwargs['widget']

            self.endpoints = []

        def paint(self, painter, option, widget=0):
            """
            Overloaded function from QGraphicsItem; determines how the item should be painted onto the screen.

            :param painter: A QPainter object, which manages low-level painting functions and includes a QPen and
                            QBrush for managing color, fill, and line style, among others.
            :param option: A QStyleOptionGraphicsItem instance Qt uses to store the options used when drawing the item.
            :param widget: The QWidget to paint on

            :type painter: PyQt4.QtGui.QPainter
            :type option: PyQt4.QtGui.QStyleOptionGraphicsItem
            :type widget: PyQt4.QtGui.QWidget

            :return: None
            """
            # Remove default Qt selection behavior
            tempop = option
            tempop.state &= not qg.QStyle.State_Selected
            qg.QGraphicsLineItem.paint(self, painter, tempop, widget)

        def itemChange(self, change, value):
            if change == qg.QGraphicsItem.ItemSelectedChange:
                # Note: Need to use '==' operator for condition to evaluate correctly. (Qt will cast the QVariant
                # 'value' to a boolean when evaluating only if the boolean equivalent operator is used.)
                if value == 1:
                    self.widget.edges[self.idx].setSelect(True)
                else:
                    self.widget.edges[self.idx].setSelect(False)
            return qg.QGraphicsLineItem.itemChange(self, change, value)

    class Edge:
        def __init__(self, **kwargs):
            self.widget = None
            self.idx = None
            self.dfentry = None
            self.edge_segs = []
            self.slabs = []
            self._selected = False
            if 'widget' in kwargs:
                self.widget = kwargs['widget']
            if 'idx' in kwargs:
                self.idx = kwargs['idx']
            if 'dfentry' in kwargs:
                self.dfentry = kwargs['dfentry']
            if 'edge_segs' in kwargs:
                self.edge_segs = kwargs['edge_segs']
            if 'slabs' in kwargs:
                self.slabs = kwargs['slabs']

        def setSelect(self, selected):
            self._selected = selected
            for es in self.edge_segs:
                if selected:
                    es.setPen(qg.QPen(qg.QColor(255, 105, 255), 3, qc.Qt.SolidLine, qc.Qt.RoundCap))
                else:
                    es.setPen(qg.QPen(qc.Qt.red, 1, qc.Qt.SolidLine, qc.Qt.RoundCap))
            for s in self.slabs:
                if selected:
                    s.setBrush(qg.QColor(255, 105, 255))
                    s.setPen(qg.QPen(qg.QColor(255, 105, 255), 4, qc.Qt.SolidLine, qc.Qt.RoundCap))
                else:
                    s.setBrush(qc.Qt.cyan)
                    s.setPen(qg.QPen(qc.Qt.cyan, 4, qc.Qt.SolidLine, qc.Qt.RoundCap))

        def isSelected(self):
            return self._selected
