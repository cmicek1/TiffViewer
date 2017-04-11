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
            s = sp.DrawingPointsWidget.Slab(0.0, 0.0, rectWidth, rectHeight, dfentry=slab, widget=self.parent,
                                            parent_idx_name='edgeIdx')
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

        slab_parent_idx_name = 'edgeIdx'
        node_parent_list_name = 'edgeList'

        # Calculate min slice in range
        d1 = int(self.parent.browser.z - offset)
        prev = d1 - 1
        if d1 < 0:
            d1 = 0
            prev = None

        # If scrolling down, hide items in previous uppermost visible slice (if not selected)
        self.hide_slice(prev, 'down', lnIdx_attrName=slab_parent_idx_name, ptParent_attrName=node_parent_list_name)

        # Calculate max slice of range
        d2 = int(self.parent.browser.z + offset)
        nxt = d2 + 1
        if d2 > self.parent.browser.stack.maxz:
            d2 = int(self.parent.browser.stack.maxz)
            nxt = None

        # If scrolling up, hide items in previous lowermost visible slice
        self.hide_slice(nxt, 'up', lnIdx_attrName=slab_parent_idx_name, ptParent_attrName=node_parent_list_name)

        # Check scale out of scope so the current stored scale can be modified
        scale = float(self.parent.browser.splitter.width()) / self.parent.browser.stack.imarray.shape[1]

        if resize:
            self.resize()

        self.display(d1, d2, lnIdx_attrName=slab_parent_idx_name)

        self.parent.cur_scale = scale
