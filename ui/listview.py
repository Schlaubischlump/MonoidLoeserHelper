import bisect

from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex, QVariant
from PyQt5.QtWidgets import QListView


class ModelNotInitializedException(Exception):
    pass


class DataModel(QAbstractListModel):
    """
    Simple data model which manages data in the format: [(a1, b1, ...), (a2, b2, ...), ...]. For each position inside
    a tuple of the list a Qt role is defined to interact with the data.
    See the ListView documentation to better understand how to interact with the data.
    """

    AllRole = Qt.UserRole + 1

    def __init__(self, display_index, data, parent=None):
        super(DataModel, self).__init__(parent)

        self.list_data = data
        # Check state for each row
        self._checked_rows = [Qt.Unchecked] * len(data)

        # Index of the tuple item for QDisplayRole
        self._display_index = display_index

        self.resetRoles()

    def flags(self, index):
        """
        :return new flags including the a flag to display a checkbox on the left side of the data
        """
        return super(DataModel, self).flags(index) | Qt.ItemIsUserCheckable

    def rowCount(self, parent=QModelIndex()):
        """
        :return the total number of rows
        """
        return len(self.list_data)

    def data(self, index, role=Qt.DisplayRole):
        """
        Read a specific data entry.
        :param index: index (row) of the data to change
        :param role: specific role which should be changed (there is a role for each header)
        """
        try:
            entry = self.list_data[index.row()]
        except IndexError:
            return QVariant()

        if role == Qt.DisplayRole:
            return entry[self._display_index]
        elif role == DataModel.AllRole:
            return entry
        elif role == Qt.CheckStateRole:
            return self._checked_rows[index.row()]
        elif role in self._roles:
            idx = self._role_indices[role]
            return entry[idx]

        return QVariant()

    def setData(self, index, value, role=Qt.DisplayRole):
        """
        Update data according to a specific role and update the UI.
        :param value: new value for this role
        :param index: index (row) of the data to change
        :param role: specific role which should be changed (there is a role for each header)
        """
        entry = self.list_data[index.row()]

        if role == Qt.DisplayRole:
            entry[self._display_index] = value
        elif role == DataModel.AllRole:
            entry = value
        elif role == Qt.CheckStateRole:
            self._checked_rows[index.row()] = value
        elif role in self._roles:
            idx = self._role_indices[role]
            entry[idx] = value
        else:
            return super(DataModel, self).setData(index, value, role)

        # update UI
        self.dataChanged.emit(index, index)
        return True

    def insertData(self, row, value):
        """
        Insert a new data entry at a given index.
        :param row: row to insert the data at
        :param value: new value to isert
        """
        self.beginInsertRows(QModelIndex(), row, row)
        self.list_data.insert(row, value)
        self._checked_rows.insert(row, False)
        self.endInsertRows()

    def removeData(self, row):
        """
        Remove data entry at a specific row.
        :param row: number of row to remove
        """
        self.beginRemoveRows(QModelIndex(), row, row)
        self.list_data.pop(row)
        self._checked_rows.pop(row)
        self.endRemoveRows()

    def registerRole(self, name, data_index):
        """
        Register a new role.
        :param name: name for this role
        :param data_index: index inside a data tuple to return for this role
        :return new role
        """
        self._last_role_idx += 1
        role = Qt.UserRole + self._last_role_idx

        self._roles[role] = name
        self._role_indices[role] = data_index

        return role

    def resetRoles(self):
        """
        Delete all registered roles.
        """
        self._roles = {DataModel.AllRole: "all"}
        self._role_indices = {}
        self._last_role_idx = 1

    def roleNames(self):
        """
        :return a list with all role names
        """
        return self._roles


class ListView(QListView):
    """
    Simple list view class which displays only one entry with a checkbox per row, but manages the remaing data as well.
    E.g you should provide data in the format [(name1, grade1, ...), (name2, grade2, ...), ...]. You can then define a
    display_index which will be shown inside the list. If you would choose 0, only the first tuple entry meaning
    name1, name2,... will be shown inside the list, but a reference to the rest of the data is saved as well.

    What the ListView will look like for:

    display_index=0    or    display_index=1:

    -----------              -----------
    ☐ name1                  ☐ grade1
    -----------              -----------
    ☐ name2                  ☐ grade2
    -----------              -----------
    ....                     ....

    By providing a header list you can describe the data for each element of a tuple. You can use this header to
    change a specific data entry. For the above example the following header might be choosen: ["Name", "Grade", ...].
    The header will not be shown inside the UI. It is only used for referring to the data.


    Some examples of how to read and set data:

    Calling: data(0) -> (name1, grade1, ...)
    Calling: data(1) -> (name2, grade2, ...)
    Calling: data(0, header="Name") -> name1
    Calling: data(1, header="Grade") -> grade2

    Calling: setData(0, N_A_M_E_3, header="Name") -> [(N_A_M_E_3, grade1, ...), (name2, grade2, ...), ...]
    Calling: setData(1, G_R_A_D_E_3, header="Grade") -> [(name1, grade1, ...), (name2, G_R_A_D_E_3, ...), ...]
    """

    def __init__(self, headers=None, data=None, display_index=0, parent=None):
        super(ListView, self).__init__(parent)

        self._selection_callback = None
        self._data = []

        if headers and data:
            self.updateData(headers, data, display_index)

        # connect each header to a specific role
        self._header_roles = {}

    def selectionCallback(self):
        """
        Callback function for selection change.
        """
        return self._selection_callback

    def setSelectionCallback(self, cb):
        """
        Change function to call when the current selection changes.
        :param cb: new callback function
        """
        self._selection_callback = cb

        if self.selectionModel() and cb:
            self.selectionModel().selectionChanged.connect(cb)

    def addDataInOrder(self, value):
        """
        Add a new entry with a given value for the QDisplayRole in alphabetical order
        :param value: new value for QDisplayRole
        """
        model = self.model()

        # Insert the new user in the sidebar in alphabetical order.
        names = [d[model._display_index].lower() for d in self._data]
        row = bisect.bisect(names, value.lower())

        # New information about the user.
        user_info = ["-"]*len(self._headers)
        user_info[model._display_index] = value

        # Add new Information to the model.
        model.insertData(row, user_info)

        # Select the new user.
        self.setCurrentRow(row)

    def removeSelectedData(self):
        """
        Remove the currently selected data from the list.
        """
        row = self.currentRow()
        if row >= 0:
            self.model().removeData(row)

    def hasData(self):
        """
        :return True if the listview is not empty otherwise False.
        """
        return len(self._data) > 0

    def setData(self, row, value, header=None):
        """
        Change the data entry at a specific row (and header).
        :param row: index of the row
        :param header: name of the header for which to return the data (None to change the whole entry)
        """
        if header is None:
            role = DataModel.AllRole
        else:
            role = self._header_roles[header]

        model = self.model()
        index = model.index(row)
        model.setData(index, value, role)

    def data(self, row, header=None):
        """
        Return the data for a specific row (and header).
        :param row: index of the row
        :param header: name of the header for which to return the data (None to receive the whole entry)
        """
        model = self.model()
        index = model.index(row)
        if header is None:
            role = DataModel.AllRole
        else:
            role = self._header_roles[header]
        return model.data(index, role)

    def updateData(self, headers, data, display_index):
        """
        Call this methode if the data changes.
        :param headers: new header values
        :param data: new data
        :param display_index: index inside the data tuple to display
        """
        self._data = data

        model = DataModel(display_index, data)
        self.setModel(model)

        self.updateHeaders(headers)

        if self.selectionModel() and self.selectionCallback():
            self.selectionModel().selectionChanged.connect(self.selectionCallback())

    def updateHeaders(self, headers):
        """
        Call this method if the header data changes.
        :param headers: new headers
        """
        if not isinstance(self.model(), DataModel):
            raise ModelNotInitializedException("You must call updateData at least once before calling updateHeaders.")

        self._header_roles = {}
        self._headers = headers

        # register a role for each header
        for i, h in enumerate(headers):
            self._header_roles[h] = self.model().registerRole(h+"Role", i)

    def allHeaders(self):
        """
        :return a list of all headers
        """
        return self._headers

    def allData(self):
        """
        :return a list of all the data in the format: [(a1, b1, ...), (a2, b2, ...), ...]
        """
        return self._data

    def selectedData(self):
        """
        :return a list with all selected data entries in the format: [(a1, b1, ...), (a2, b2, ...), ...]
        """
        model = self.model()

        checked_data = []
        for row in range(model.rowCount()):
            index = model.index(row)
            if model.data(index, Qt.CheckStateRole) == Qt.Checked:
                checked_data.append(model.data(index, DataModel.AllRole))
        return checked_data

    def setCurrentRow(self, row):
        """
        Change the currently selected row.
        :param row: new row to select
        """
        if self.hasData():
            model = self.model()
            index = model.index(row)
            if index:
                self.setCurrentIndex(index)

    def currentRow(self):
        """
        :return the index of the currently selected row or -1 if none is selected
        """
        index = self.currentIndex()
        return index.row() if index else -1

    def checkedRows(self):
        """
        :return indices of all checked rows
        """
        model = self.model()

        checked_rows = []
        for row in range(model.rowCount()):
            index = model.index(row)
            if model.data(index, Qt.CheckStateRole) == Qt.Checked:
                checked_rows.append(row)
        return checked_rows

    def setCheckedRows(self, rows):
        """
        Select all specified rows. Invalid row indices will be ignored.
        :param rows: list with all row indices to select
        """
        model = self.model()
        num_rows = model.rowCount()

        # Filter all valid rows from the list.
        rows = [v for v in sorted(rows) if 0 <= v < num_rows]

        for row in range(num_rows):
            index = model.index(row)
            # Check or uncheck the row.
            state = Qt.Unchecked
            if rows and row == rows[0]:
                rows.pop(0)
                state = Qt.Checked
            model.setData(index, state, Qt.CheckStateRole)
