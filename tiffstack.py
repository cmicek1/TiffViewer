import os
import tifffile as tf
import pandas as pd
import nodedb as nd


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
        self.node_db = nd.NodeDb(
            pd.read_csv(self.directory.split('ch')[0] + 'nT.txt'), DX, DY)

    @property
    def maxz(self):
        """
        The index of the last image in the stack.

        :return: The depth of the stack

        :rtype: int
        """
        return self.imarray.shape[0] - 1
