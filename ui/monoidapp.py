import os
import sys
import pickle
from webbrowser import open_new_tab
from collections import namedtuple

from PyQt5.QtCore import QFileInfo, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMessageBox, QAction, QFileDialog, QInputDialog

from util import DEFAULT_FILE, SAVED_APP_STATE_FILE
from util.helper import export_data_to_file
from util.parser import parse_php_file
from util.config import load_settings, save_settings

from .monoidmainwindow import MonoidMainWindow
from .monoidaboutwindow import MonoidAboutWindow
from .monoidpreferenceswindow import MonoidPreferencesWindow


class MonoidApp(QApplication):

    @staticmethod
    def applicationName():
        return QFileInfo(QCoreApplication.applicationFilePath()).fileName()

    @staticmethod
    def showError(error_title, error_msg):
        """
        Show an error dialog and exit the program.
        :param error_title: title of the error message
        :param error_msg: informative text for this error
        """
        msg = QMessageBox()
        msg.setText(error_title)
        msg.setInformativeText(error_msg)
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def __init__(self, *args, **kwargs):
        """
        Override the default constructor to create a main window.
        """
        super().__init__(*args, **kwargs)

        self.setStyle("fusion")

        # Load the main application settings.
        self.settings = load_settings()

        # Create the about window.
        self.about_win = MonoidAboutWindow(self)

        # Create Preferences window.
        self.pref_win = MonoidPreferencesWindow(self)

        # Create a main window.
        self.win = MonoidMainWindow(self)

        # Setup menu items.
        self.createMenubar()

    def saveSettings(self):
        """
        Save the current settings to a file.
        """
        save_settings(self.settings)

    def setData(self, headers, users):
        """
        Fill the list with all the necessary data.
        :param headers: header information
        :param users: user information
        """
        self.win.populate(headers, users)

    def createMenubar(self):
        """
        Create the menubar with open, export and tools options.
        """
        def showAboutWindow():
            """
            Show the applications about window.
            """
            self.about_win.raise_()
            self.about_win.show()

        def showPreferencesWindow():
            """
            Show the applications preferences window.
            """
            self.pref_win.raise_()
            self.pref_win.show()

        def openPhpFile():
            """
            Open an existing php file.
            """
            path, _ = QFileDialog.getOpenFileName(self.win, "Open file:", "./", "Php Files(*.php)")
            if path:
                try:
                    headers, data = parse_php_file(path)
                except:
                    self.showError("Corrupt file.", "Error parsing the file: {0}. Make sure the file is a "\
                                   "valid php file.".format(path))
                else:
                    self.setData(headers, data)

        def export():
            """
            Export all data into a php file.
            """
            path, _ = QFileDialog.getSaveFileName(self.win, "Export file:", DEFAULT_FILE)
            if path:
                headers = self.win.user_list.allHeaders()
                data = self.win.user_list.allData()
                export_data_to_file(path, headers, data)

        def exportSelected():
            """
            Export all selected data to a php file.
            """
            path, _ = QFileDialog.getSaveFileName(self.win, "Export file:", DEFAULT_FILE)
            if path:
                headers = self.win.user_list.allHeaders()
                data = self.win.user_list.selectedData()
                export_data_to_file(path, headers, data)

        def changeReleaseNumber():
            """
            Change the Monoid release number.
            """
            headers = self.win.user_list.allHeaders()
            default_value = int(headers[self.settings.header.point_indices.start])
            num, ok = QInputDialog.getInt(self.win, "New release number", "Enter the first monoid "\
                                            "release number for this year:", default_value, 0)
            if ok:
                # Change the release numbers for the whole year.
                for i, idx in enumerate(self.settings.header.point_indices):
                    headers[idx] = str(num + i)
                self.win.user_list.updateHeaders(headers)
                self.win.updateHeaderLabels()

        # About window.
        about_action = QAction("&About {0}".format(self.applicationName()), self)
        about_action.setMenuRole(QAction.AboutRole)
        about_action.triggered.connect(showAboutWindow)

        # Preference window.
        preference_action = QAction("&Preferences...", self)
        preference_action.setShortcut("Meta+,")
        preference_action.setMenuRole(QAction.PreferencesRole)
        preference_action.triggered.connect(showPreferencesWindow)

        # Import and export actions.
        open_php_action = QAction("&Open php file...", self)
        open_php_action.setShortcut("Ctrl+O")
        open_php_action.setStatusTip("Open an exported php file.")
        open_php_action.triggered.connect(openPhpFile)

        export_action = QAction("&Export...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.setStatusTip("Export the data to a php file.")
        export_action.triggered.connect(export)

        export_selected_action = QAction("&Export selected...", self)
        export_selected_action.setShortcut("Ctrl+Shift+E")
        export_selected_action.setStatusTip("Export the selected data to a php file.")
        export_selected_action.triggered.connect(exportSelected)

        # Useful tools to change existing data.
        change_release_action = QAction("&Change monoid release number", self)
        change_release_action.setShortcut("Ctrl+R")
        change_release_action.setStatusTip("Change the monoid release number.")
        change_release_action.triggered.connect(changeReleaseNumber)

        menubar = self.win.menuBar()

        # Default file menu.
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(open_php_action)
        file_menu.addAction(export_action)
        file_menu.addAction(export_selected_action)

        # Tools menu.
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction(change_release_action)

        # Edit menu, which contains about and preferences menu on platforms different to macOS.
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(about_action)
        edit_menu.addAction(preference_action)

        help_menu = menubar.addMenu("&Help")
        help_menu.addAction("View Source Code", lambda: open_new_tab("https://github.com/Schlaubischlump"))

    def showWindow(self):
        """
        Show the main Application window.
        """
        self.win.show()

    def saveApplicationState(self):
        """
        Save the current application state (including selections) in a pickle file.
        """
        headers = self.win.user_list.allHeaders()
        data = self.win.user_list.allData()
        checked_rows = self.win.user_list.checkedRows()
        pickle_data = {"headers": headers, "user_data": data, "checked_rows": checked_rows}
        with open(SAVED_APP_STATE_FILE, "wb") as f:
            pickle.dump(pickle_data, f)

    def restoreApplicationState(self):
        """
        Try to restore the last application state.
        :return True on success False otherwise.
        """
        try:
            pickle_in = open(SAVED_APP_STATE_FILE, "rb")
            pickle_data = pickle.load(pickle_in)
            # Load the data from the last application state.
            self.setData(pickle_data["headers"], pickle_data["user_data"])
            self.win.user_list.setCheckedRows(pickle_data["checked_rows"])
            # Sucessfully restored the last application state.
            return True
        except:
            return False

    def deleteApplicationState(self):
        """
        Delete the currently save application state.
        :return True on success, otherwise False
        """
        try:
            os.remove(SAVED_APP_STATE_FILE)
            return True
        except:
            return False
