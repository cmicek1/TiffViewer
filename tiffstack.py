import os
import tifffile as tf
import pandas as pd
import nodedb as nd
import slabdb as sd
import edgedb as ed


NODE_DIR = 'nodes'
SLAB_DIR = 'slabs'
EDGE_DIR = 'edges'

# Scaling factor to go from um data to pixels for rendering
# (number below is in um/pixel).
DX = 0.216
DY = 0.216


class TiffStack:
    """
    Helper class for easy viewing of 3D TIFF stacks.
    Requires TiffFile package.
    """
    def __init__(self, directory):
        """
        Constructor; loads image.

        :param directory: Directory of the image to load,
                          or file path if not a child of
                          the working directory.

        :type directory: str
        """
        self.directory = directory
        self.fname = os.path.basename(self.directory)
        _ = self.fname.split('_')
        self.date, self.animal, self.stacknum, self.channel = (
            _[0], _[1], int(_[2]), _[3].split('.')[0])
        self.image = tf.TiffFile(self.directory)
        self.imarray = self.image.asarray()
        self.dx, self.dy = DX, DY
        self._node_dir = '{0}/{1}/{2}'.format(
            os.path.dirname(self.directory),
            NODE_DIR, self.fname.split('ch')[0] + 'nT.txt')
        self._slab_dir = '{0}/{1}/{2}'.format(
            os.path.dirname(self.directory),
            SLAB_DIR, self.fname.split('ch')[0] + 'sD.txt')
        self._edge_dir = '{0}/{1}/{2}'.format(
            os.path.dirname(self.directory),
            EDGE_DIR, self.fname.split('ch')[0] + 'eT.txt')
        self.node_db = nd.NodeDb(pd.read_csv(self._node_dir), DX, DY)
        self.slab_db = sd.SlabDb(pd.read_csv(self._slab_dir), DX, DY)
        self.edge_db = ed.EdgeDb(pd.read_csv(self._edge_dir))

    @property
    def maxz(self):
        """
        The index of the last image in the stack.

        :return: The depth of the stack

        :rtype: int
        """
        return self.imarray.shape[0] - 1
