class EdgeDb:
    """
    Pandas DataFrame of graph nodes, representing vascular junctions.
    """
    def __init__(self, dataframe):
        """
        Constructor; allows user interaction with database.

        :param dataframe: Pandas DataFrame of edge data from CSV txt file.

        :type dataframe: pandas.DataFrame
        """
        self.dframe = dataframe
