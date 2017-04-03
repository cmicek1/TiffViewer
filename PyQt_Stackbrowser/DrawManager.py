class DrawManager(object):
    def __init__(self, parent, mode=None):
        self.parent = parent
        self.mode = mode

    def setup(self, *args):
        pass

    def draw(self, *args):
        pass

    def hide_slice(self, sliceZ, scroll_dir, **kwargs):

        lnIdx_attrName = None
        ptParent_attrName = None

        if 'lnIdx_attrName' in kwargs:
            lnIdx_attrName = kwargs['lnIdx_attrName']

        if 'ptParent_attrName' in kwargs:
            ptParent_attrName = kwargs['ptParent_attrName']

        if sliceZ is not None:
            if sliceZ in self.parent.slabs:
                for s in self.parent.slabs[sliceZ]:
                    lnIdx = getattr(s.dfentry, lnIdx_attrName)
                    try:
                        if not self.parent.edges[lnIdx].isSelected():
                            s.hide()
                        if s.dfentry.edgeIdx in self.parent.edge_segs:
                            for es in self.parent.edge_segs[lnIdx]:
                                cond = None
                                if scroll_dir == 'down':
                                    cond = es.endpoints[0].dfentry.z <= sliceZ and (
                                        es.endpoints[1].dfentry.z <= sliceZ) and not (
                                        self.parent.edges[es.idx].isSelected())
                                elif scroll_dir == 'up':
                                    cond = es.endpoints[0].dfentry.z >= sliceZ and (
                                        es.endpoints[1].dfentry.z >= sliceZ) and not (
                                        self.parent.edges[es.idx].isSelected())
                                if cond:
                                    es.hide()
                    except KeyError:
                        pass

            if sliceZ in self.parent.nodes:
                for n in self.parent.nodes[sliceZ]:
                    eList = getattr(n.dfentry, ptParent_attrName)
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

    def resize(self):
        # Check scale out of scope so the current stored scale can be modified
        scale = float(self.parent.browser.splitter.width()) / self.parent.browser.stack.imarray.shape[1]
        # Scale all items (both visible and invisible) via a linear iteration through each member dict,
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

    def display(self, top, bot, **kwargs):

        lnIdx_attrName = None

        if 'lnIdx_attrName' in kwargs:
            lnIdx_attrName = kwargs['lnIdx_attrName']

        for z in range(top, bot + 1):
            visible_edges = []
            if z in self.parent.slabs:
                for s in self.parent.slabs[z]:
                    lnIdx = getattr(s.dfentry, lnIdx_attrName)
                    try:  # Faster to handle exceptions than check slabs
                        _ = self.parent.edge_segs[lnIdx]
                        s.show()
                        if s.dfentry.edgeIdx not in visible_edges:
                            visible_edges.append(lnIdx)
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
