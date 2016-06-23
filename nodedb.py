import pandas as pd


class NodeDb:
    """
    Pandas DataFrame of graph nodes, representing vascular junctions.
    """
    def __init__(self, dataframe, dx, dy):
        self.dframe = dataframe
