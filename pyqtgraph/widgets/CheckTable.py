# -*- coding: utf-8 -*-
from ..Qt import QtGui, QtCore
from . import VerticalLabel

__all__ = ['CheckTable']

class CheckTable(QtGui.QWidget):
    """Table of check boxes.

    Example usage:

    .. testsetup:: *

        import pyqtgraph as pg
        pg.mkQApp()

    .. testcode::

        # handle user interaction with checkboxes
        def onCheckChange(row, col, checked):
            print("box in row named {} had a state change".format(row))

        tab = pg.CheckTable(["col1", "col2"])
        tab.addRow("row1")
        tab.sigStateChanged.connect(onCheckChange)

    Parameters
    ----------
    columns :
        Column names. Each is displayed as a :class:`~pyqtgraph.VerticalLabel` at the
        top of the table.

    Attributes
    ----------
    sigStateChanged : (str, str, bool)
        Emits the row name, column name, and checked state when a check box in the table
        is checked/unchecked.
    """
    
    sigStateChanged = QtCore.Signal(object, object, object) # (row, col, state)
    
    def __init__(self, columns: list[str]):
        QtGui.QWidget.__init__(self)
        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.headers = []
        self.columns = columns
        col = 1
        for c in columns:
            label = VerticalLabel.VerticalLabel(c, orientation='vertical')
            self.headers.append(label)
            self.layout.addWidget(label, 0, col)
            col += 1
        
        self.rowNames = []
        self.rowWidgets = []
        self.oldRows = {}  ## remember settings from removed rows; reapply if they reappear.

    def updateRows(self, rows: list[str]):
        """Update the list of row names.

        If a row is already in the table, it is unaffected. Existing rows not provided
        are removed via :meth:`removeRow` (i.e. they are cached).
        """
        for r in self.rowNames[:]:
            if r not in rows:
                self.removeRow(r)
        for r in rows:
            if r not in self.rowNames:
                self.addRow(r)

    def addRow(self, name: str):
        """Add a row to the table.

        Parameters
        ----------
        name :
            Row name. This is displayed as a label to the left of the row of checkboxes.
        """
        label = QtGui.QLabel(name)
        row = len(self.rowNames)+1
        self.layout.addWidget(label, row, 0)
        checks = []
        col = 1
        for c in self.columns:
            check = QtGui.QCheckBox('')
            check.col = c
            check.row = name
            self.layout.addWidget(check, row, col)
            checks.append(check)
            if name in self.oldRows:
                check.setChecked(self.oldRows[name][col])
            col += 1
            check.stateChanged.connect(self.checkChanged)
        self.rowNames.append(name)
        self.rowWidgets.append([label] + checks)
        
    def removeRow(self, name: str):
        """Remove a row from the table.

        Removed rows are cached such that if :meth:`addRow` is subsequently called with
        the same name, the states of the row's checkboxes are restored.

        Parameters
        ----------
        name :
            The row to remove.
        """
        row = self.rowNames.index(name)
        self.oldRows[name] = self.saveState()['rows'][row]  ## save for later
        self.rowNames.pop(row)
        for w in self.rowWidgets[row]:
            w.setParent(None)
            if isinstance(w, QtGui.QCheckBox):
                w.stateChanged.disconnect(self.checkChanged)
        self.rowWidgets.pop(row)
        for i in range(row, len(self.rowNames)):
            widgets = self.rowWidgets[i]
            for j in range(len(widgets)):
                widgets[j].setParent(None)
                self.layout.addWidget(widgets[j], i+1, j)

    def checkChanged(self, state):
        check = QtCore.QObject.sender(self)
        self.sigStateChanged.emit(check.row, check.col, state)
        
    def saveState(self) -> dict:
        """Save the state of the table as a dict.

        The state can be subsequently passed to :meth:`restoreState` to restore the
        state of the table.
        """
        rows = []
        for i in range(len(self.rowNames)):
            row = [self.rowNames[i]] + [c.isChecked() for c in self.rowWidgets[i][1:]]
            rows.append(row)
        return {'cols': self.columns, 'rows': rows}
        
    def restoreState(self, state: dict):
        """Restore the state of the table.

        Typically, this is called with the output of :meth:`saveState`, though it may
        also be used to quickly instantiate a table with non-default checked states:

        .. testcode::

            tab = pg.CheckTable(["col1", "col2"])
            tab.restoreState({"rows": [["row1", True, False], ["row2", True, True]]})
        """
        rows = [r[0] for r in state['rows']]
        self.updateRows(rows)
        for r in state['rows']:
            rowNum = self.rowNames.index(r[0])
            for i in range(1, len(r)):
                self.rowWidgets[rowNum][i].setChecked(r[i])
