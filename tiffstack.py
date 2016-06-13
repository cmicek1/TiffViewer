import tifffile as tf


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
        self.image = tf.TiffFile(self.directory)

    @property
    def getarray(self):
        """
        Get array representation of the stack.

        :return: An array of shape (z, x, y)

        :rtype: array
        """
        return self.image.asarray()

    @property
    def maxz(self):
        """
        The index of the last image in the stack.

        :return: The depth of the stack

        :rtype: int
        """
        return self.getarray.shape[0] - 1
