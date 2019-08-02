"""
QShortcutEditor. 

A PySide2 widget to display and configure an application's shortcuts.
Can be tested as a standalone program (although it only has one shortcut).


Typical usage, call it from your QMainWindow::

    class MyGUI(QMainWindow):
       # ...
       def customizeShortcuts(self):
            from QShortcutEditor import QShortcutEditor
            ed = QShortcutEditor()
            ed.prepare(self)
            ed.show()
            # keep a reference otherwise it disappears immediately
            self._shortcut_editor = d
"""


from PySide2 import QtCore, QtGui, QtWidgets


class QShortcutEditor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(400,600)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.table = QtWidgets.QTableWidget(5, 2, self)
        self.verticalLayout.addWidget(self.table)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(True)
        self.table.setHorizontalHeaderLabels(['Shortcut', 'Action'])
        self.table.verticalHeader().setVisible(False)
        
        self.setWindowTitle("Customize shortcuts")
#        self.setWindowIcon(pkgIcon('escale.png'))
        act = QtWidgets.QAction("Close", self)
        act.setShortcuts([QtGui.QKeySequence(QtCore.Qt.Key_Escape)])
        act.triggered.connect(self.close)
        self.addAction(act)


    def prepare(self, gui):
        "List all shortcuts from the given widget, to be ready for a show()."
        # ignore actions that don't have a shortcut
        actions = [ action for action in gui.findChildren(QtWidgets.QAction)
                    if (len(action.shortcuts()) > 0) ]
        #print(actions)
        tab = self.table
        tab.setRowCount(len(actions))

        actions.sort(key=lambda act: act.shortcuts()[0].toString())
        
        for (irow, action) in enumerate(actions):
            tip = action.toolTip()
            short = action.shortcuts()[0].toString()
            x = QtWidgets.QTableWidgetItem()
            x.setText(short)
            tab.setItem(irow, 0, x)
    
            x = QtWidgets.QTableWidgetItem()
            x.setText(tip)
            tab.setItem(irow, 1, x)
            

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    ed = QShortcutEditor()
    ed.prepare(ed)
    ed.show()

    sys.exit(app.exec_())
