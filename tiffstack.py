import os
import tifffile as tf
import Tkinter as Tk
import tkFileDialog
import pandas as pd
import igraph as ig
import nodedb as nd
import slabdb as sd
import edgedb as ed
import stackdb

NODE_DIR = 'nodes'
SLAB_DIR = 'slabs'
EDGE_DIR = 'edges'

STACKDB_DIR = '../stackdb'
LINE_DIR = '../line'

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

        if len(_) == 3:
            try:
                self.date, self.animal, self.channel = (_[0], _[1], _[2].split('.')[0])
            except IndexError:
                pass
            self.type = 'Spines'
            self.image = tf.TiffFile(self.directory)
            self.imarray = self.image.asarray()
            self._stackdb_dir = '{0}/{1}/{2}'.format(
                os.path.dirname(self.directory),
                STACKDB_DIR, self.fname.split('ch')[0] + 'db2.txt')
            self._line_dir = '{0}/{1}/{2}'.format(
                os.path.dirname(self.directory),
                LINE_DIR, self.fname.split('ch')[0] + 'l.txt')
            self.stack_db = stackdb.StackDb(self._stackdb_dir)
        if len(_) == 4:
            try:
                self.date, self.animal, self.stacknum, self.channel = (
                    _[0], _[1], int(_[2]), _[3].split('.')[0])
            except IndexError:
                pass
            self.type = 'Vascular'
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
            self.dx, self.dy = DX, DY

    def load(self, attr):
        """
        Universal loading function; can reload any class attribute if stored in a file.

        :param attr: The name of the attribute to load.
        :type attr: str

        :return: None
        """
        to_load = makedialog('~/Desktop')
        if attr in self.__dict__.keys():
            if attr.endswith('db'):
                to_load = pd.read_csv(to_load)
                if self.type == 'Vascular' and attr in ['node_db', 'slab_db']:
                    n = self.__dict__[attr].__class__(to_load, DX, DY)
                    print(n)
                    self.__dict__[attr] = n
                else:
                    n = self.__dict__[attr].__class__(to_load)
                    self.__dict__[attr] = n

    def get_slice(self, z):
        """
        Returns the stack slice at the requested z-value

        :param z: The depth of the stack slice being requested

        :type z: int

        :return: The requested slice

        :rtype: numpy.ndarray[][][int]
        """
        if 0 <= z <= self.maxz:
            return self.imarray[z]

    @property
    def maxz(self):
        """
        The index of the last image in the stack.

        :return: The depth of the stack

        :rtype: int
        """
        return self.imarray.shape[0] - 1

    def tograph(self):
        g = ig.Graph()
        g.add_vertices(self.node_db.dframe.shape[0])
        for field in list(self.node_db.dframe):
            if not self.node_db.dframe[field].isnull().values.any():
                g.vs[field] = self.node_db.dframe[field].as_matrix().tolist()
            else:
                temp = self.node_db.dframe[field].as_matrix().tolist()
                g.vs[field] = [str(i) for i in temp]
        for edge in self.edge_db.dframe.itertuples():
            g.add_edges([(int(edge.targetIdx), int(edge.sourceIdx))])

            slabs = str(self.slab_db.dframe.loc[self.slab_db.dframe['edgeIdx'] == edge.i].T.to_dict().values())
            g.es[edge.i]['Slabs'] = slabs

        for field in list(self.edge_db.dframe):
            if not self.edge_db.dframe[field].isnull().values.any():
                g.es[field] = self.edge_db.dframe[field].as_matrix().tolist()
            else:
                temp = self.edge_db.dframe[field].as_matrix().tolist()
                g.es[field] = [str(i) for i in temp]

        g.write_graphml(self.fname.split('_ch')[0] + '.graphml')

        return g


def adjust_contrast(stack_slice, new_min, new_max):
    """
    Convenience function that performs contrast stretching on a single slice of the stack. Stretches the image
    histogram to fall within the privided minimum and maximum intensities.

    :param stack_slice: An unaltered slice from the original stack
    :param new_min: The new minimum intensity
    :param new_max: The new maximum intensity

    :type stack_slice: numpy.array[][][int]
    :type new_min: int
    :type new_max: int

    :return: The requested slice with adjusted contrast
    :rtype: numpy.ndarray[][][int]
    """
    stack_slice = (stack_slice - new_min * 1.0) * 255 / (new_max - new_min)
    stack_slice[stack_slice <= 0] = 0
    stack_slice[stack_slice >= 255] = 255
    return stack_slice.astype('uint8')


def new():
    """
    Way to create stack outside of browser. Select a valid TIFF stack to begin.

    :return: the stack
    """
    fpath = makedialog('~/Desktop')
    stack = TiffStack(fpath)
    return stack


def makedialog(default_dir):
    """
    Create a dialog box for file selection.

    :param default_dir: The default directory of the dialog box.
    :type default_dir: str

    :return: The file path
    :rtype: str
    """
    root = Tk.Tk()
    root.attributes('-topmost', True)
    root.withdraw()
    fpath = tkFileDialog.askopenfilename(
        initialdir=os.path.expanduser(default_dir))
    return fpath
