import PyQt4.QtCore as qc


class PointTable(qc.QAbstractTableModel):
    def __init__(self, data, parent=None):
        super(PointTable, self).__init__(parent)
        self._data = data

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._data.values)

    def columnCount(self, parent=None, *args, **kwargs):
        return self._data.columns.size

    def data(self, index, role=qc.Qt.DisplayRole):
        if index.isValid():
            if role == qc.Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
        return None

    def headerData(self, col, orientation, role=None):
        if orientation == qc.Qt.Horizontal and role == qc.Qt.DisplayRole:
            return self._data.columns[col]
        return None
