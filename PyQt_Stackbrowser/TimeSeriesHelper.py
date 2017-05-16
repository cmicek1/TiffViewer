import pandas as pd


class TimeSeriesHelper:
    """
    Class to help with mapping data between time points for time series data.
    """
    def __init__(self, window1, window2=None):
        """
        Initializer for the TimeSeriesHelper instance. Currently tied explicitly to at least two MainWindow instances
        (although one may be None), but can with a bit of Python wizardry be tied to an arbitrary number of windows
        at some point. Could be a list of windows, but since this class needs to be instantiated before the windows
        actually contain anything, indexing into such a list later would likely be problematic. So they're attributes
        for now.
        :param window1: The initial window to link to the helper; mandatory
        :param window2: The second window to link. By default is None, but should be set once a counterpart to the
                        first is created.

        :type window1: stackbrowserQt.MainWindow
        :type window2: stackbrowserQt.MainWindow
        """
        self.window1 = window1
        self.window2 = window2
        self.map = None

    def setup_map(self):
        if self.window1.stack.type == 'Spines':
            self.map = pd.read_table(self.window1.stack.directory)
