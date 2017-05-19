import pandas as pd
import PyQt4.QtCore as qc
import PyQt4.QtGui as qg
import PointTable as pt


class TimeSeriesHelper:
    """
    Class to help with mapping data between time points for time series data.
    """
    def __init__(self, window1, window2=None):
        """
        Initializer for the TimeSeriesHelper instance. Currently tied explicitly to at least two MainWindow instances
        (although one may be None), with functions to add/delete windows from the window dictionary contained herein 
        provided. Windows are stored in the win_dict attribute of this class, with each window as a value associated
        with a unique key ID.
        :param window1: The initial window to link to the helper; mandatory
        :param window2: The second window to link. By default is None, but should be set once a counterpart to the
                        first is created.

        :type window1: stackbrowserQt.MainWindow
        :type window2: stackbrowserQt.MainWindow
        """
        self.windict = {window1.id: window1}
        if window2 is not None:
            self.windict.update({window2.id: window2})
        self.map = None
        self.map_table = None

    def setup_map(self, id_num):
        """
        Load the mapping through time of connected points into a Pandas DataFrame and a QTableView. This function looks
        for a file called tseries.txt in the root folder of the stack. The file is tab-delimited, with the first row
        holding the number of each time point, and each cell holding a node/spine index. All spines in a row are 
        considered identical.
        
        :param id_num: The ID number of the first window created for the application (used for clarifying 
                       type-specific behavior)
        :type id_num: int
        :return: None
        """
        if self.windict[id_num].stack.type == 'Spines':
            stack = self.windict[id_num].stack
            self.map = pd.read_table(stack.directory.split(stack.fname)[0] + '/../tseries.txt')
            self.map_table = qg.QTableView()
            self.map_table.setModel(pt.PointTable(self.map))
            self.map_table.setWindowFlags(self.map_table.windowFlags() | qc.Qt.Window)
            self.map_table.setFont(qg.QFont("Arial", 10))
            self.map_table.setSelectionBehavior(qg.QAbstractItemView.SelectRows)
            self.map_table.selectionModel().selectionChanged.connect(lambda selected, deselected,
                                                                     func=self.table_select: func(selected, deselected))

    def add_window(self, window):
        """
        Add a window to the window dictionary (should be called when a new window is created)
        :param window: The MainWindow to add to the dictionary
        :type window: stackbrowserQt.MainWindow
        :return: None
        """
        self.windict.update({window.id: window})

    def delete_window(self, window):
        """
        Delete a window to the window dictionary (should be called whenever a window is closed)
        :param window: The MainWindow to add to the dictionary
        :type window: stackbrowserQt.MainWindow
        :return: None
        """
        del self.windict[window.id]

    def show_table(self):
        """
        Displays the mapping created in setup_map as a table in a new window.
        :return: None
        """
        if self.map_table is not None:
            self.map_table.show()

    def table_select(self, selected, deselected):
        """
        Custom slot defining selection behavior for the point map table. Selection of any row will select the 
        corresponding nodes/spines in all open time points.
        :param selected: The row(s) selected
        :param deselected: The row(s) deselected since the last call
        
        :type selected: PyQt4.QtGui.QItemSelection
        :type deselected: PyQt4.QtGui.QItemSelection
        
        :return: None
        """
        for ID, win in self.windict.iteritems():
            for node in selected.indexes():
                if win.stack.stacknum == node.column():
                    idx = self.map.iloc[node.row(), node.column()]
                    if not pd.np.isnan(idx):
                        try:
                            n = win.points.nodes_by_idx[int(idx)]
                            n.show()
                            if not n.isSelected():
                                n.setSelected(True)
                        except KeyError:
                            pass

            for node in deselected.indexes():
                if win.stack.stacknum == node.column():
                    idx = self.map.iloc[node.row(), node.column()]
                    if not pd.np.isnan(idx):
                        try:
                            n = win.points.nodes_by_idx[int(idx)]
                            if n.isSelected():
                                n.setSelected(False)
                        except KeyError:
                            pass
