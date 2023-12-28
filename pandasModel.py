from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pandas as pd

class pandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame()):
        super().__init__()
        self.df = df

    def rowCount(self, parent=None):
        return self.df.shape[0]

    def columnCount(self, index=None):
        return self.df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return str(self.df.iloc[index.row(), index.column()])
        if role == Qt.DecorationRole :
            if index.column() == self.df.columns.get_loc('Result') :
                if self.df.iloc[index.row(), index.column()] == 'True' :
                    return QColor('blue')
                elif self.df.iloc[index.row(), index.column()] == 'False' :
                    return QColor('red')
                else :
                    return QImage('yellow')
        return QVariant()

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable 

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        if role == Qt.EditRole:
            self.df.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            return self.df.columns[section]
        elif orientation == Qt.Vertical:
            return str(self.df.index[section])
