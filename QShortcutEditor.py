# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Copyright (C) 2019-2020 Jean-Didier Garaud
# This file's most recent version can be retrieved at:
#    https://github.com/JeanDidierGaraud/snippets/blob/master/QShortcutEditor.py


"""
PySide2 widgets to display and configure an application's shortcuts.

Provides QShortcutViewer and QShortcutEditor.

For the impatient: type `python3 -m QShortcutEditor` to see them in action.

Typical usage, call it from your QMainWindow::

    class MyGUI(QMainWindow):
       # ...
       def customizeShortcuts(self):
            from QShortcutEditor import QShortcutEditor
            ed = QShortcutEditor(gui=self)
            ed.show()
            # keep a reference, otherwise it may be garbage-collected too soon:
            self._shortcut_editor = ed

Look at the ``if __name__ == "__main__":`` block of this file for a complete usage (popup window or dockable widget).

Note: it also works with PyQt5, just change the from...import statement.
"""

__version__ = '1.0.0'

# See also: https://stackoverflow.com/questions/57328901/list-all-shortcuts-of-a-qmainwindow
#
# TODO:
#   - improve the 2-parts modify_shortcut, it seems weird to have to do this
#   - decide whether more than 2 shortcuts is necessary, if yes allow to change the 3rd or 4th; currently 3+ shortcuts are allowed, but can only change the first two
#   - click on column order to sort
#   - allow to remove a shortcut (right click? or little cross? del or backspace?); in qt-5.12, qkeysequenceedit.cpp:77, a TODO announces a "clear button"
#   - add a save/load mechanism
#   - warn if shortcuts are conflicting, when the window is closed
#   - add a statusbar for this warning messages or statusTip
#   - would QTableView be a better design?
#   - keeping a ref on the _gui is not very OO; allowing to only pass the list of actions would be better?
#   - add buttons apply/close/cancel


from PySide2 import QtCore, QtGui, QtWidgets
#from PyQt5 import QtCore, QtGui, QtWidgets


class QShortcutViewer(QtWidgets.QWidget):
    def __init__(self, gui=None, parent=None):
        super().__init__(parent)
        self.resize(400,600)

        self.columns = ['Shortcut', 'Alternate', 'Description']

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.table = QtWidgets.QTableWidget(5, 3, self)
        self.verticalLayout.addWidget(self.table)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setVisible(True)
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.verticalHeader().setVisible(False)

        self.setWindowTitle("Shortcuts")

        act = QtWidgets.QAction("Close", self)
        act.setShortcuts([QtGui.QKeySequence(QtCore.Qt.Key_Escape)])
        act.triggered.connect(self.close)
        self.addAction(act)

        self._gui = gui

    def _all_actions(self):
        "Prepare the list of interesting actions."
        self._actions = [ action for action in self._gui.findChildren(QtWidgets.QAction)
                    if (len(action.shortcuts()) > 0) ]

    def _uniq_sort(self):
        "Sort and remove duplicates in the given list of actions."
        # now let's remove duplicates (e.g. when an action is in a menu and a context menu)
        # unfortunately using a set doesn't work:  actions = list(set(actions))
        # even though their repr/str is equal (so I guess the C++ QAction is indeed the same)
        # let's use the repr of the actions to do the comparison:
        # uniqactions = { repr(a): a for a in actions }
        # actions2 = list(uniqactions.values())
        # well, it turns out that the duplicates were my mistake. Still, looking for incoherent or duplicates
        # would be interesting. I keep the dict-by-comprehension trick, might turn out useful sometimes later.
        # The _hash below could also be useful.
        actions2 = list(set(self._actions))

        # Sorting is a little tricky when we click the display_all_actions box:
        # actions.sort(key=lambda act: act.shortcuts()[0].toString())
        # actions.sort(key=lambda act: "" if not act.shortcuts() else act.shortcuts()[0].toString())
        actions2.sort(key=lambda act: [ x.toString() for x in act.shortcuts()])
        self._actions = actions2

    def _prepare(self):
        "List all shortcuts from the given widget, to be ready for a show()."

        try:   # just a little cosmetics:
            self.setWindowIcon(gui.windowIcon())
        except:
            pass

        self._all_actions()
        self._uniq_sort()

        #print(actions)
        tab = self.table
        tab.clearContents()
        tab.setRowCount(len(self._actions))

        for (irow, action) in enumerate(self._actions):
            tip = action.toolTip()
            #short = action.shortcuts()[0].toString()
            ## again, if display_all, we need this precaution:
            short = "" if not action.shortcuts() else action.shortcuts()[0].toString()
            alt = [ a.toString() for a in action.shortcuts()[1:] ]
            x = QtWidgets.QTableWidgetItem()
            x.setText(short)
            x.setFlags(x.flags() ^ QtCore.Qt.ItemIsEditable)
            tab.setItem(irow, self.columns.index('Shortcut'), x)

            x = QtWidgets.QTableWidgetItem()
            x.setText(' '.join(alt))   # this will display the 3rd shortcut of an action; but with current code, you'll never manage to change it
            x.setFlags(x.flags() ^ QtCore.Qt.ItemIsEditable)
            tab.setItem(irow, self.columns.index('Alternate'), x)

            x = QtWidgets.QTableWidgetItem()
            x.setText(tip)
            x.setFlags(x.flags() ^ QtCore.Qt.ItemIsEditable)
            x.setToolTip(action.statusTip())
            tab.setItem(irow, self.columns.index('Description'), x)

    def show(self):
        self._prepare()
        super().show()


class QShortcutEditor(QShortcutViewer):
    def __init__(self, gui=None, parent=None):
        super().__init__(gui, parent)
        self.setWindowTitle("Customize shortcuts")

        # could use QTableWidget.sortItems to allow sorting?
        self.display_all_actions = QtWidgets.QCheckBox('All')
        self.display_all_actions.setToolTip('Hide/display actions that do not (yet) have a shortcut')
        self.verticalLayout.addWidget(self.display_all_actions)
        self.display_all_actions.toggled.connect(self._prepare)
        #self.table.itemDoubleClicked[QtWidgets.QTableWidgetItem].connect(self.modify_shortcut)
        self.table.cellDoubleClicked[int,int].connect(self.modify_shortcut)
        self.currently_modifying = None

        self.button_print = QtWidgets.QPushButton('Print shortcuts')
        self.button_print.setToolTip('Print shortcuts to the console (only the modified ones)')  # copy-to-cliboard would be a lot smarter!
        self.verticalLayout.addWidget(self.button_print)
        self.button_print.clicked.connect(lambda: print(self.pickle()))
        #self.button_print.clicked.connect(lambda: self.save('my_saved_shortcuts.py'))

        # store the initial shortcuts, to be able to tell which were customized
        actions = [ action for action in self._gui.findChildren(QtWidgets.QAction)
                    if (len(action.toolTip()) > 0) ]
        self._initial_shortcuts = {
            self._hash(a): a.shortcuts()
            for a in actions }

    def _all_actions(self):
        """Prepare the list of configurable actions.

        Uses the checkbox whether to ignore or display actions that don't have a shortcut.
        If an action neither has tooltip nor shortcut, it's probably not interesting, so we filter them out.
        """
        if self.display_all_actions.isChecked():
            actions = [ action for action in self._gui.findChildren(QtWidgets.QAction)
                        if (len(action.toolTip()) > 0) ]
        else:
            actions = [ action for action in self._gui.findChildren(QtWidgets.QAction)
                        if (len(action.shortcuts()) > 0) ]

        self._actions = actions

    def modify_shortcut(self, row, column):
        if column == self.columns.index('Description'): return  # don't want to modify the tooltip

        if self.currently_modifying is not None: return # we're currently modifying another one
        # this could be nicer by detecting a focusOut event in the QKeySequenceEdit, with e.g. QApplication::focusChanged

        action = self._actions[row]

        # Note: maybe want to play with QAbstractItemView::EditTriggers (https://doc.qt.io/qt-5/qabstractitemview.html), to allow only double-click?

        # not exactly correct if we have 3 shortcuts, but it's a good start and ok for 1 or 2 shortcuts:
        shorts = action.shortcuts()


        # note that QKeySequenceEdit allow emacs-style shortcuts :-D
        x = QtWidgets.QKeySequenceEdit("", self)
        self.currently_modifying = (action, x, column - self.columns.index('Shortcut'))
        self.table.setCellWidget(row, column, x)
        x.editingFinished.connect(self.modify_shortcut_end)
        x.show()
        x.setFocus()

    def modify_shortcut_end(self):
        # fixme: don't really like to split the function in 2... could do better?
        # currently not nice if the user double clicks elsewhere before changing the shortcut
        action, x, column = self.currently_modifying
        shorts = action.shortcuts()
        new_short = x.keySequence()
        try:
            shorts[column] = new_short
        except IndexError:
            shorts.append(new_short)
        action.setShortcuts(shorts)

        x.close()
        self._prepare()   # to update the table
        self.currently_modifying = None

    def _hash(self, action):
        "Return a hash of the given QAction."
        # The hash should be anything reproducible between runs
        # Pitfall: if someone fixes a typo in the statusTip, the hash changes...
        return (action.toolTip(), action.statusTip())

    def pickle(self):
        "Return a pickable representation of the *modified* shortcuts."
        db = {}
        for a in self._actions:
            h = self._hash(a)
            if a.shortcuts() != self._initial_shortcuts[h]:
                db[h] = [ s.toString() for s in a.shortcuts() ]
        return db

    def unpickle(self, actions, db):
        "Modify shortcuts given the db (a dictionary, typically saved previously by `pickle`)."
        for a in actions:
            h = self._hash(a)
            try:
                a.setShortcuts(db[h])
            except KeyError as e:
                pass

    def _prepare(self):
        super()._prepare()

    def save(self, filename):
        fic = open(filename, 'w')
        db = self.pickle()
        # if db:
        #     print(db)
        # else:
        #     print('Shortcuts have not been modified')
        fic.write('shortcuts = %s\n'%repr(db))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    # let's build a quick widget:
    gui = QtWidgets.QMainWindow()

    gui.setWindowTitle('Simple test')
    menuFile = gui.menuBar().addMenu("&File")

    action = QtWidgets.QAction("Quit", gui)
    action.setShortcuts([ QtGui.QKeySequence.Quit,
                          QtGui.QKeySequence(QtCore.Qt.Key_Escape),
                          'Ctrl+B'   # as in byebye, to see how triple shortcuts work
    ])
    action.triggered.connect(gui.close)
    menuFile.addAction(action)

    menu_edit = gui.menuBar().addMenu("&Tools")

    action_view = QtWidgets.QAction("View shortcuts...", gui)
    menu_edit.addAction(action_view)
    action_view.setShortcuts(['F1'])
    action_view.setStatusTip('View shortcuts')
    # To work properly, the QShortcutEditor should be constructed after the gui has attached all its actions.
    # ... hmmm, there's a bit of chicken and egg issue here: need ed to triggered.connect,
    #     but need the action to be already in the menu so I can assign it a shortcut ????
    viewer = QShortcutViewer(gui)
    action_view.triggered.connect(viewer.show)

    action_edit = QtWidgets.QAction("Edit shortcuts...", gui)
    menu_edit.addAction(action_edit)
    action_edit.setShortcuts(['F2'])
    action_edit.setStatusTip('View and edit shortcuts')
    editor = QShortcutEditor(gui)
    action_edit.triggered.connect(editor.show)

    toolbar = gui.addToolBar("Main toolbar")  # notice that menus and toolbar have non-shortcut-actions
    toolbar.addAction(action_view)
    toolbar.addAction(action_edit)

    gui.setCentralWidget(QtWidgets.QLabel(' Hit F1 to display shortcuts. \n Hit F2 to view and edit them. \n Hit Esc to quit.'))


    # # # this is the dockable version:
    # it = QtWidgets.QDockWidget("View/Edit shortcuts", gui)
    # it.setObjectName("dockShortcutEditor")
    # it.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
    # ed2 = QShortcutEditor(parent=it, gui=gui)
    # it.setWidget(ed2)
    # gui.addDockWidget(QtCore.Qt.RightDockWidgetArea, it)

    gui.show()

    actions = [ action for action in gui.findChildren(QtWidgets.QAction)
                if (len(action.toolTip()) > 0) ]
    editor.unpickle(actions,
                    {('View shortcuts', 'View shortcuts'): ['F1', 'F3', 'F4']}  # to see how multiple shortcuts work
    )

    sys.exit(app.exec_())
