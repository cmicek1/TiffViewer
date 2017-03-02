import PyQt4.QtCore as qc
import PyQt4.QtGui as qg
import StackPoints as sp


class VascManager:
    """
    Helper class to deal with drawing points for the 'Vascular' mode of the stack browser.
    """
    def __init__(self, parent):
        self.parent = parent

    def setup_slabs(self, xfactor, yfactor, xtranslate, ytranslate, rectWidth, rectHeight, slab_pen, slab_brush):

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
