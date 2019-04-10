from functools import partial

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QListWidgetItem, QGridLayout, QLabel, QLineEdit, QMainWindow, \
                            QPushButton, QInputDialog

from util.helper import str_to_points, points_to_str
from .listview import ListView


class MonoidMainWindow(QMainWindow):
    """
    Main monoid application window.
    """

    def updateTextfieldAtPosition(self, row, value):
        """
        Update textfield information inside the grid layout.
        :param row: row inside the grid (starting at 0)
        :param value: new value
        """
        text_field = self.user_info_grid.itemAtPosition(row+1, 1).widget()
        text_field.setText(value)
        text_field.setCursorPosition(0)

    def userSelectionChanged(self):
        """
        Called when the selection inside the user list changes.
        """
        self.selectUser(self.user_list.currentRow())

    def showAddUserDialog(self):
        """
        Insert the a new user in alphabetical order in the sidebar.
        """
        text, ok = QInputDialog.getText(self, "New student", "Enter the students name:")
        if ok:
            self.user_list.addDataInOrder(text)

            if self.user_list.hasData():
                self.user_info_widget.show()

    def removeSelectedUser(self):
        """
        Remove the currently selected user from the list.
        """
        self.user_list.removeSelectedData()

        if not self.user_list.hasData():
            self.user_info_widget.hide()

    def __init__(self, app, *args, **kwargs):
        super(MonoidMainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Monoid")
        # Keep a reference to the application.
        self.app = app

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Main window layout.
        hbox = QHBoxLayout(main_widget)

        # Create a list with all users.
        user_list_widget = QWidget()
        list_container_grid = QGridLayout()
        user_list_widget.setLayout(list_container_grid)

        self.user_list = ListView()
        self.user_list.setSelectionMode(ListView.SingleSelection)
        self.user_list.setSelectionCallback(self.userSelectionChanged)

        add_bt = QPushButton("+")
        add_bt.clicked.connect(self.showAddUserDialog)
        remove_bt = QPushButton("-")
        remove_bt.clicked.connect(self.removeSelectedUser)

        list_container_grid.addWidget(self.user_list, 0, 0, 1, -1)
        list_container_grid.addWidget(add_bt, 1, 0)
        list_container_grid.addWidget(remove_bt, 1, 1)

        # Create a widget to display detailed information about a user.
        self.user_info_widget = QWidget()
        self.user_info_grid = QGridLayout()
        self.user_info_widget.setLayout(self.user_info_grid)

        # Add list and detailed view to the window.
        hbox.addWidget(user_list_widget)
        hbox.addWidget(self.user_info_widget)

    def populate(self, headers, users):
        """
        Fill the list with all the necessary data.
        :param headers: header information
        :param users: user information
        """
        def cleanup_text(text_field):
            """
            Insert a "-" if the text_field is empty.
            :param text_field: reference to the connected text_field
            """
            if text_field.text() == "":
                text_field.setText("-")

        # Fill the list with all user names.
        name_idx = headers.index(self.app.settings.header.name_field)
        self.user_list.updateData(headers, users, name_idx)

        # Hide detailed view if no data is available.
        if not self.user_list.hasData():
            self.user_info_widget.hide()

        # Clear the current user_info grid.
        while self.user_info_grid.count():
            child = self.user_info_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add all info fields based on the current header.
        sum_idx = headers.index(self.app.settings.header.sum_field)
        for i, h in enumerate(headers, 1):
            self.user_info_grid.addWidget(QLabel(h), i, 0)

            widget = QLineEdit("-")
            if i-1 in self.app.settings.header.point_indices:
                widget.textChanged.connect(self.updateSumLabel)
            elif i-1 == sum_idx:
                # Disbale editing the sum field
                widget.setReadOnly(True)
                widget.setEnabled(False)
                widget.setStyleSheet("QLineEdit{background-color: rgba(0, 0, 0, 0); color: black; border: 0px}")

            # Connect all necessary text change events and add the widget to the view hierachy.
            widget.editingFinished.connect(partial(cleanup_text, widget))
            widget.textChanged.connect(partial(self.updateDataModel, i-1))

            self.user_info_grid.addWidget(widget, i, 1)

        # Select the first user in the list.
        self.user_list.setCurrentRow(0)


    def selectUser(self, user_index):
        """
        Display detailed information about the currently selcted user
        :param data: current user data
        """
        # Display the user information.
        for i in range(self.user_info_grid.rowCount()-1):
            headers = self.user_list.allHeaders()
            value = self.user_list.data(user_index, header=headers[i])
            self.updateTextfieldAtPosition(i, value)

        # Calculate new sum.
        self.updateSumLabel()

    def updateSumLabel(self):
        """
        Update the sum value based on the currently entered values.
        """
        row = self.user_list.currentRow()

        # Automaticlly calculate new sum value based on entered values.
        points_field = [self.user_info_grid.itemAtPosition(i+1, 1).widget() for i in self.app.settings.header.point_indices]
        expected = sum(str_to_points(text_field.text()) for text_field in points_field)
        new_value = points_to_str(expected)

        # Update user Interface with new value.
        headers = self.user_list.allHeaders()
        sum_idx = headers.index(self.app.settings.header.sum_field)
        label = self.user_info_grid.itemAtPosition(sum_idx+1, 1).widget()
        label.setText(new_value)

    def updateHeaderLabels(self):
        """
        Update the labels on the left side in the detailed view.
        """
        headers = self.user_list.allHeaders()
        lablels = [self.user_info_grid.itemAtPosition(i+1, 0).widget() for i in range(len(headers))]
        for l, h in zip(lablels, headers):
            l.setText(h)

    def updateDataModel(self, header_index):
        """
        Update the data if the value of a textfield changes.
        :param header_index: header index to determine the corresponding textfield and header
        """
        header = self.user_list.allHeaders()[header_index]
        row = self.user_list.currentRow()
        text_field = self.user_info_grid.itemAtPosition(header_index+1, 1).widget()
        self.user_list.setData(row, text_field.text(), header=header)
