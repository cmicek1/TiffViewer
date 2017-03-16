import StackPoints as sp
import DrawManager as dm


class VascManager(dm.DrawManager):
    """
    Helper class to deal with drawing points for the 'Vascular' mode of the stack browser.
    """
    def __init__(self, parent):
        super(dm.DrawManager, self).__init__()
        self.parent = parent

    def setup(self, loc_params, rectSize, draw_tools):
        self.setup_slabs(loc_params, rectSize, draw_tools)
        self.setup_nodes(loc_params, rectSize, draw_tools)
        self.setup_edges()

    def setup_slabs(self, loc_params, rectSize, draw_tools):
        xfactor = loc_params[0]
        yfactor = loc_params[1]
        xtranslate = loc_params[2]
        ytranslate = loc_params[3]

        rectWidth = rectSize[0]
        rectHeight = rectSize[1]

        slab_pen = draw_tools[0][0]
        slab_brush = draw_tools[0][1]

        edge_pen = draw_tools[1]

        # Place all items in the correct position, and store them in dicts
        time = 0
        prev_slab = None
        prev_pos = (0, 0)

        for slab in self.parent.browser.stack.slab_db.dframe.itertuples():
            s = sp.DrawingPointsWidget.Slab(0.0, 0.0, rectWidth, rectHeight, dfentry=slab, widget=self.parent)
            xpos = slab.x * xfactor / self.parent.browser.stack.dx + xtranslate
            ypos = slab.y * yfactor / self.parent.browser.stack.dy + ytranslate
            s.setPos(xpos - rectWidth/2, ypos - rectHeight/2)  # Note: Coordinates for QGraphicsEllipseItems are the
                                                               # upper-left corner of the item's bounding box,
                                                               # so need to translate to center
            s.setPen(slab_pen)
            s.setBrush(slab_brush)
            s.setZValue(s.zValue() + 1)
            s.hide()

            if slab.z not in self.parent.slabs:
                self.parent.slabs[slab.z] = [s]
            else:
                self.parent.slabs[slab.z].append(s)
            self.parent.browser.scene.addItem(s)

            time, prev_slab, prev_pos = self._connect_slabs(time, prev_slab, prev_pos, s, (xpos, ypos), edge_pen)

    def _connect_slabs(self, time, prev_slab, prev_pos, cur_slab, cur_pos, edge_pen):
        # Connect each Slab that has a neighbor of the same edge index with an EdgeSegment
        entry = cur_slab.dfentry
        if time == 0:
            prev_slab = cur_slab
            prev_xpos = cur_pos[0]
            prev_ypos = cur_pos[1]
            time += 1
        else:
            if entry.edgeIdx == prev_slab.dfentry.edgeIdx and (
                        entry.i == prev_slab.dfentry.i + 1):
                # Connect
                es = sp.DrawingPointsWidget.EdgeSegment(0.0, 0.0, 0.0, 0.0, idx=entry.edgeIdx, widget=self.parent)
                es.endpoints = [prev_slab, cur_slab]
                es.setLine(prev_pos[0], prev_pos[1], cur_pos[0], cur_pos[1])
                es.setPen(edge_pen)
                es.hide()
                if entry.edgeIdx not in self.parent.edge_segs:
                    self.parent.edge_segs[entry.edgeIdx] = [es]
                else:
                    self.parent.edge_segs[entry.edgeIdx].append(es)
                self.parent.browser.scene.addItem(es)
            prev_slab = cur_slab
            prev_xpos = cur_pos[0]
            prev_ypos = cur_pos[1]
            time += 1

        return time, prev_slab, (prev_xpos, prev_ypos)

    def setup_nodes(self, loc_params, rectSize, draw_tools):
        xfactor = loc_params[0]
        yfactor = loc_params[1]
        xtranslate = loc_params[2]
        ytranslate = loc_params[3]

        rectWidth = rectSize[0]
        rectHeight = rectSize[1]

        node_pen = draw_tools[2][0]
        node_brush = draw_tools[2][1]

        for node in self.parent.browser.stack.node_db.dframe.itertuples():
            n = sp.DrawingPointsWidget.Node(0.0, 0.0, rectWidth, rectHeight, dfentry=node, widget=self.parent)
            xpos = node.x * xfactor / self.parent.browser.stack.dx + xtranslate
            ypos = node.y * yfactor / self.parent.browser.stack.dy + ytranslate
            n.setPos(xpos - rectWidth/2, ypos - rectHeight/2)
            n.setPen(node_pen)
            n.setBrush(node_brush)
            n.setZValue(n.zValue() + 1)
            n.hide()
            if node.z not in self.parent.nodes:
                self.parent.nodes[node.z] = [n]
            else:
                self.parent.nodes[node.z].append(n)
            self.parent.nodes_by_idx[node.i] = n
            self.parent.browser.scene.addItem(n)

    def setup_edges(self):
        for edge in self.parent.browser.stack.edge_db.dframe.itertuples():
            idx = edge.i
            try:
                e = sp.DrawingPointsWidget.Edge(widget=self.parent, idx=idx, dfentry=edge,
                                                edge_segs=self.parent.edge_segs[idx])
                e.source = self.parent.nodes_by_idx[e.dfentry.sourceIdx]
                e.target = self.parent.nodes_by_idx[e.dfentry.targetIdx]
                for seg in e.edge_segs:
                    for ep in seg.endpoints:
                        if ep not in e.slabs:
                            e.slabs.append(ep)
                self.parent.edges[idx] = e
            except KeyError:
                pass

    def draw(self, resize=False):
        """
        Function to determine which items to show in the current browser view. Checks for Nodes and Slabs in the
        current z slice +/- an offset value (1 slice by default), and EdgeSegments that have any visible endpoints,
        and displays them. Also rescales all items if the window is resized.

        :param resize: A boolean indicating if the call for this function occurred during a resize event.

        :type resize: bool

        :return: None
        """

        # If overlay is not visible, do nothing
        if not self.parent.isVisible:
            return

        # Else, set offset from current z to search for items to be shown
        offset = self.parent.offset

        # Calculate min slice in range
        d1 = int(self.parent.browser.z - offset)
        prev = d1 - 1
        if d1 < 0:
            d1 = 0
            prev = None

        # TODO: Make this function more modular - split into chunks!
        # If scrolling down, hide items in previous uppermost visible slice (if not selected)
        if prev is not None:
            if prev in self.parent.slabs:
                for s in self.parent.slabs[prev]:
                    try:
                        if not self.parent.edges[s.dfentry.edgeIdx].isSelected():
                            s.hide()
                        if s.dfentry.edgeIdx in self.parent.edge_segs:
                            for es in self.parent.edge_segs[s.dfentry.edgeIdx]:
                                if es.endpoints[0].dfentry.z <= prev and es.endpoints[1].dfentry.z <= prev and not (
                                    self.parent.edges[es.idx].isSelected()
                                ):
                                    es.hide()
                    except KeyError:
                        pass

            if prev in self.parent.nodes:
                for n in self.parent.nodes[prev]:
                    eList = n.dfentry.edgeList
                    selected = False
                    if not eList != eList:
                        eList = eList.split(';')[0:-1]
                        for idx in eList:
                            try:
                                if self.parent.edges[int(idx)].isSelected():
                                    selected = True
                            except KeyError:
                                pass
                    if not n.isSelected() and not selected:
                        n.hide()

        # Calculate max slice of range
        d2 = int(self.parent.browser.z + offset)
        nxt = d2 + 1
        if d2 > self.parent.browser.stack.maxz:
            d2 = int(self.parent.browser.stack.maxz)
            nxt = None

        # If scrolling up, hide items in previous lowermost visible slice
        if nxt is not None:
            if nxt in self.parent.slabs:
                for s in self.parent.slabs[nxt]:
                    try:
                        if not self.parent.edges[s.dfentry.edgeIdx].isSelected():
                            s.hide()
                        if s.dfentry.edgeIdx in self.parent.edge_segs:
                            for es in self.parent.edge_segs[s.dfentry.edgeIdx]:
                                if es.endpoints[0].dfentry.z >= nxt and es.endpoints[1].dfentry.z >= nxt and not (
                                    self.parent.edges[es.idx].isSelected()
                                ):
                                    es.hide()
                    except KeyError:
                        pass

            if nxt in self.parent.nodes:
                for n in self.parent.nodes[nxt]:
                    eList = n.dfentry.edgeList
                    selected = False
                    if not eList != eList:
                        eList = eList.split(';')[0:-1]
                        for idx in eList:
                            try:
                                if self.parent.edges[int(idx)].isSelected():
                                    selected = True
                            except KeyError:
                                pass
                    if not n.isSelected() and not selected:
                        n.hide()

        # Check scale out of scope so the current stored scale can be modified
        scale = float(self.parent.browser.splitter.width()) / self.parent.browser.stack.imarray.shape[1]

        if resize:  # Scale all items (both visible and invisible) via a linear iteration through each member dict,
            # so scales of all items are easy to keep track of
            for k in self.parent.slabs:
                for s in self.parent.slabs[k]:
                    s.setPos(s.pos() / self.parent.cur_scale * scale)
            for idx in self.parent.edge_segs:
                # Handle error case of edge with one slab (shouldn't occur, but can if there was an error in the
                # creation of the initial text file)
                try:
                    for es in self.parent.edge_segs[idx]:
                        temp = es.line()
                        temp.setPoints(es.line().p1() / self.parent.cur_scale * scale,
                                       es.line().p2() / self.parent.cur_scale * scale)
                        es.setLine(temp)
                except KeyError:
                    pass
            for k in self.parent.nodes:
                for n in self.parent.nodes[k]:
                    n.setPos(n.pos() / self.parent.cur_scale * scale)

        for z in range(d1, d2 + 1):
            visible_edges = []
            if z in self.parent.slabs:
                for s in self.parent.slabs[z]:
                    try:  # Faster to handle exceptions than check slabs
                        _ = self.parent.edge_segs[s.dfentry.edgeIdx]
                        s.show()
                        if s.dfentry.edgeIdx not in visible_edges:
                            visible_edges.append(s.dfentry.edgeIdx)
                    except KeyError:
                        pass

                for idx in visible_edges:
                    try:
                        for es in self.parent.edge_segs[idx]:
                            if es.endpoints[0].isVisible() or es.endpoints[1].isVisible():
                                es.show()
                    except KeyError:
                        pass

            if z in self.parent.nodes:
                for n in self.parent.nodes[z]:
                    n.show()

        self.parent.cur_scale = scale
