import PyQt4.QtCore as qc
import PyQt4.QtGui as qg
import VascManager as vm


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

        self.nodes_by_idx = {}

        # Want to pass reference to keep z up-to-date
        self.browser = browser
        self.drawManager = None
        if self.browser.stack.type == 'Vascular':
            self.drawManager = vm.VascManager(self)
        self.scaleFactor = 1  # fraction of total
        self.isVisible = 1  # Show all points and edges by default
        self.offset = 1

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

        # If opening a new file, delete all currently active items
        for item in self.browser.scene.items():
            if item.parentItem() is None and not item.isWidget():
                self.browser.scene.removeItem(item)
                del item

        # Create pens and brushes to color nodes, slabs, and edges
        slab_pen = qg.QPen(qc.Qt.cyan, 4, qc.Qt.SolidLine, qc.Qt.RoundCap)
        slab_brush = qg.QBrush(qc.Qt.cyan)

        edge_pen = qg.QPen(qc.Qt.red, 1, qc.Qt.SolidLine, qc.Qt.RoundCap)

        node_pen = qg.QPen(qc.Qt.red, 7, qc.Qt.SolidLine, qc.Qt.RoundCap)
        node_brush = qg.QBrush(qc.Qt.red)

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

        loc_params = (xfactor, yfactor, xtranslate, ytranslate)
        rectSize = (rectWidth, rectHeight)
        draw_tools = ((slab_pen, slab_brush), edge_pen, (node_pen, node_brush))

        self.drawManager.setup(loc_params, rectSize, draw_tools)

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
        offset = self.offset

        # Calculate min slice in range
        d1 = int(self.browser.z - offset)
        prev = d1 - 1
        if d1 < 0:
            d1 = 0
            prev = None

        # If scrolling down, hide items in previous uppermost visible slice (if not selected)
        if prev is not None:
            if prev in self.slabs:
                for s in self.slabs[prev]:
                    try:
                        if not self.edges[s.dfentry.edgeIdx].isSelected():
                            s.hide()
                        if s.dfentry.edgeIdx in self.edge_segs:
                            for es in self.edge_segs[s.dfentry.edgeIdx]:
                                if es.endpoints[0].dfentry.z <= prev and es.endpoints[1].dfentry.z <= prev and not (
                                    self.edges[es.idx].isSelected()
                                ):
                                    es.hide()
                    except KeyError:
                        pass

            if prev in self.nodes:
                for n in self.nodes[prev]:
                    eList = n.dfentry.edgeList
                    selected = False
                    if not eList != eList:
                        eList = eList.split(';')[0:-1]
                        for idx in eList:
                            try:
                                if self.edges[int(idx)].isSelected():
                                    selected = True
                            except KeyError:
                                pass
                    if not n.isSelected() and not selected:
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
                    try:
                        if not self.edges[s.dfentry.edgeIdx].isSelected():
                            s.hide()
                        if s.dfentry.edgeIdx in self.edge_segs:
                            for es in self.edge_segs[s.dfentry.edgeIdx]:
                                if es.endpoints[0].dfentry.z >= nxt and es.endpoints[1].dfentry.z >= nxt and not (
                                    self.edges[es.idx].isSelected()
                                ):
                                    es.hide()
                    except KeyError:
                        pass

            if nxt in self.nodes:
                for n in self.nodes[nxt]:
                    eList = n.dfentry.edgeList
                    selected = False
                    if not eList != eList:
                        eList = eList.split(';')[0:-1]
                        for idx in eList:
                            try:
                                if self.edges[int(idx)].isSelected():
                                    selected = True
                            except KeyError:
                                pass
                    if not n.isSelected() and not selected:
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
                    try:  # Faster to handle exceptions than check slabs
                        _ = self.edge_segs[s.dfentry.edgeIdx]
                        s.show()
                        if s.dfentry.edgeIdx not in visible_edges:
                            visible_edges.append(s.dfentry.edgeIdx)
                    except KeyError:
                        pass

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
            self.label = None
            if 'dfentry' in kwargs:
                self.dfentry = kwargs['dfentry']
                self.label = self._Label(self)
            if 'widget' in kwargs:
                self.widget = kwargs['widget']

        class _Label(qg.QGraphicsSimpleTextItem):
            def __init__(self, *_args):
                super(qg.QGraphicsSimpleTextItem, self).__init__(*_args)
                self.line = None
                if self.parentItem():
                    parent = self.parentItem()
                    self.setText("{}/z{}".format(parent.dfentry.i, parent.dfentry.z))
                    self.setFlags(qg.QGraphicsItem.ItemIsMovable | qg.QGraphicsItem.ItemSendsScenePositionChanges)
                    self.setFont(qg.QFont('Arial', 9))
                    self.setBrush(qg.QBrush(qc.Qt.white))
                    self.setPos(18, -18)
                    self.line = qg.QGraphicsLineItem(qc.QLineF(parent.pos() + qc.QPointF(5, -3), self.pos() +
                                                               qc.QPointF(-3, 5)), parent)
                    self.line.setPen(qg.QPen(qc.Qt.white))

            def itemChange(self, change, value):
                if change == qg.QGraphicsItem.ItemScenePositionHasChanged:
                    temp = self.line.line()
                    temp.setP2(self.line.mapFromScene(value.toPointF()) + qc.QPointF(-3, 5))
                    self.line.setLine(temp)
                return qg.QGraphicsSimpleTextItem.itemChange(self, change, value)

        def show(self):
            self.label.show()
            self.label.line.show()
            qg.QGraphicsEllipseItem.show(self)

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
            if change == qg.QGraphicsItem.ItemSelectedHasChanged:
                # Note: Need to use '==' operator for condition to evaluate correctly. (Qt will cast the QVariant
                # 'value' to a boolean when evaluating only if the boolean equivalent operator is used.)
                if value == 1:
                    self.setBrush(qc.Qt.yellow)
                    self.setPen(qg.QPen(qc.Qt.yellow, 7, qc.Qt.SolidLine, qc.Qt.RoundCap))
                    self.show()
                    self.widget.browser.action_handler('_node_select', self)
                else:
                    self.setBrush(qc.Qt.red)
                    self.setPen(qg.QPen(qc.Qt.red, 7, qc.Qt.SolidLine, qc.Qt.RoundCap))
                    self.hide()
                    self.widget.drawPoints()
                    self.widget.browser.action_handler('_node_select', self, deselect=True)
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
                    self.widget.drawPoints()
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

        def shape(self):
            """
            Overrides default QGraphicsLineItem implementation to increase the bounds of the line for easier mouse
            selection.

            :return: path, the path the item's painter will follow to draw the segment

            :rtype: qg.QPainterPath
            """
            rect = qc.QRectF(self.line().p1(), self.line().p2()).normalized()

            rect.adjust(-1, -1, 1, 1)

            path = qg.QPainterPath()
            path.addRect(rect)

            return path

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
                    self.widget.drawPoints()
            return qg.QGraphicsLineItem.itemChange(self, change, value)

    class Edge:  # Could make this an invisible QGraphicsItem if necessary
        def __init__(self, **kwargs):
            self.widget = None
            self.idx = None
            self.dfentry = None
            self.edge_segs = []
            self.slabs = []
            self.source = None
            self.target = None
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
            # Could possibly toggle component visibility below
            for es in self.edge_segs:
                if selected:
                    es.setPen(qg.QPen(qg.QColor(255, 105, 255), 3, qc.Qt.SolidLine, qc.Qt.RoundCap))
                    if not es.isVisible():
                        es.show()
                else:
                    es.setPen(qg.QPen(qc.Qt.red, 1, qc.Qt.SolidLine, qc.Qt.RoundCap))
                    es.hide()
            for s in self.slabs:
                if selected:
                    s.setBrush(qg.QColor(255, 105, 255))
                    s.setPen(qg.QPen(qg.QColor(255, 105, 255), 4, qc.Qt.SolidLine, qc.Qt.RoundCap))
                    if not s.isVisible():
                        s.show()
                else:
                    s.setBrush(qc.Qt.cyan)
                    s.setPen(qg.QPen(qc.Qt.cyan, 4, qc.Qt.SolidLine, qc.Qt.RoundCap))
                    s.hide()
            if selected:
                self.source.setBrush(qc.Qt.red)
                self.source.setPen(qg.QPen(qc.Qt.red, 7, qc.Qt.SolidLine, qc.Qt.RoundCap))
                self.source.show()

                self.target.setBrush(qc.Qt.green)
                self.target.setPen(qg.QPen(qc.Qt.green, 7, qc.Qt.SolidLine, qc.Qt.RoundCap))
                self.target.show()

            else:
                # self.source.setBrush(qc.Qt.red)
                # self.source.setPen(qg.QPen(qc.Qt.red, 7, qc.Qt.SolidLine, qc.Qt.RoundCap))
                self.source.hide()

                self.target.setBrush(qc.Qt.red)
                self.target.setPen(qg.QPen(qc.Qt.red, 7, qc.Qt.SolidLine, qc.Qt.RoundCap))
                self.target.hide()

        def isSelected(self):
            return self._selected