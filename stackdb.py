import pandas as pd


class StackDb:
    """
    Pandas DataFrame for MapManager spine points and associated metadata.
    """
    def __init__(self, fname):
        """
        Constructor; allows user interaction with database.

        :param fname: Name of the file containing stackdb info. Expected name format is XXXX_sY_db2.txt,
                      where XXXX is the session name and Y is the session number

        :type fname: str
        """
        self.data = {}
        f = open(fname)
        for pair in f.readline(-2).split(';'):
            _ = pair.split('=')
            self.data.update({_[0]: _[1]})
        self.dframe = pd.read_csv(fname, skiprows=0)
