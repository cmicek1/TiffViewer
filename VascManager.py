import PyQt4.QtCore as qc
import PyQt4.QtGui as qg
import StackPoints as sp


class VascManager:
    """
    Helper class to deal with drawing points for the 'Vascular' mode of the stack browser.
    """
    def __init__(self, parent):
        self.parent = parent

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
            s = sp.DrawingPointsWidget.Slab(0.0, 0.0, rectWidth, rectHeight, dfentry=slab, widget=self)
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
