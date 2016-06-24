import pygame as pg


class NodeDb:
    """
    Pandas DataFrame of graph nodes, representing vascular junctions.
    """
    def __init__(self, dataframe, dx, dy):
        self.dframe = dataframe
        self._dx, self._dy = dx, dy

    def draw_nodes(self, viewer, offset, xfactor=None, yfactor=None):
        if xfactor is None:
            xfactor = 1

        if yfactor is None:
            yfactor = 1

        d1 = viewer.current_slice - offset
        if d1 < 0:
            d1 = 0

        d2 = viewer.current_slice + offset
        if d2 > viewer.stack.maxz:
            d2 = viewer.stack.maxz
        nodes = self.dframe.loc[(d1 <= self.dframe['z']) &
                                (self.dframe['z'] <= d2)]
        for node in nodes.itertuples():

            # Parameters hard-coded for now.
            # TODO: Make these editable (separate class? interface later?)
            pg.draw.circle(viewer.screen, (150, 0, 0),
                           # Not a typo; x/y swapped in CSV file
                           (int(node.y * viewer.scale * xfactor / self._dx),
                            int(node.x * viewer.scale * yfactor / self._dy)), 5)
