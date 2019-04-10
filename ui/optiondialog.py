from PyQt5.QtWidgets import QDialog, QListWidget, QVBoxLayout, QPushButton

class OptionDialog(QDialog):
    """
    Simple QDialog which displays a list of options. Use getOption to get the index of the selected list item.
    """

    def __init__(self, title="", options=[], parent=None):
        super(OptionDialog, self).__init__(parent)

        self.setWindowTitle(title)

        self.option_list = QListWidget()
        self.option_list.addItems(options)
        self.option_list.setCurrentRow(0)
        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.option_list)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def getOption(self):
        """
        :return index of the currently selected list item.
        """
        return self.option_list.currentRow()
