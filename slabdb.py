class SlabDb:
    """
    Pandas DataFrame of graph nodes, representing vascular junctions.
    """
    def __init__(self, dataframe, dx, dy):
        """
        Constructor; allows user interaction with database.

        :param dataframe: Pandas DataFrame of slab data from CSV txt file.
        :param dx: scaling factor for slab x position, in um/pixel
        :param dy: scaling factor for slab y position, in um/pixel

        :type dataframe: pandas.DataFrame
        :type dx: float
        :type dy: float
        """
        self.dframe = dataframe
        self.dx = dx
        self.dy = dy
