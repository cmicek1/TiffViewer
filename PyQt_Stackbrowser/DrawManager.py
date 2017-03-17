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
