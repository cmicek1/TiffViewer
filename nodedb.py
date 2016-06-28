class NodeDb:
    """
    Pandas DataFrame of graph nodes, representing vascular junctions.
    """
    def __init__(self, dataframe, dx, dy):
        """
        Constructor; allows user interaction with database.

        :param dataframe: Pandas DataFrame of node data from CSV txt file.
        :param dx: scaling factor for node x position, in um/pixel
        :param dy: scaling factor for node y position, in um/pixel

        :type dataframe: pandas.DataFrame
        :type dx: float
        :type dy: float
        """
        self.dframe = dataframe
