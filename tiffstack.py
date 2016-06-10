import tifffile as tf


class TiffStack:
    def __init__(self, directory):
        self.directory = directory
        self.image = tf.TiffFile(self.directory)

    @property
    def getarray(self):
        return self.image.asarray()

    @property
    def maxz(self):
        return self.getarray.shape[0] - 1
