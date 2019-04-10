from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QDialog, QTabWidget, QWidget, QSpinBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, \
                            QComboBox, QCheckBox, QSizePolicy
from PyQt5.QtGui import QPixmap, QIcon

from util.config import LaunchMode


class GeneralTab(QWidget):

    def launchModeValueChanged(self, value):
        """
        Callback when the combox selection changes. If the file path is empty and LaunchMode.File is selected,
        `prepare_app_launch` will fall back to use an empty template file.
        :param value: new selection of combo box
        """
        self.settings.general.launch_mode = value

        # Update the text field and the corresponding settings.
        if value == LaunchMode.WEBSITE.value:
            self.websiteFileLabel.setText("Website url:")
            self.websiteFileField.setText(self.settings.general.website_url)
            self.websiteFileField.setCursorPosition(0)
        elif value == LaunchMode.FILE.value:
            self.websiteFileLabel.setText("File path:")
            self.websiteFileField.setText(self.settings.general.file_path)
            self.websiteFileField.setCursorPosition(0)

        # Hide / show the website field when required.
        if value == LaunchMode.RESTORE.value:
            self.websiteFileLabel.hide()
            self.websiteFileField.hide()
        else:
            self.websiteFileLabel.show()
            self.websiteFileField.show()

        self.win.updateHeight(0)

    def saveIntervalValueChanged(self, value):
        """
        Called when the save interval spin box value changes.
        """
        self.settings.general.save_interval = value

    def websiteFileFieldChanged(self, text):
        """
        Called when the text of the website / file field changes.
        :param text: new entered text value
        """
        # Save the new webiste url or the new file path.
        if self.launchOpt.currentIndex() == 0:
            self.settings.general.website_url = text
        elif self.launchOpt.currentIndex() == 1:
            self.settings.general.file_path = text

    def enableSplashScreenStateChanged(self, state):
        """
        Called when the enable splash screen option changes.
        :param state: new state Qt.Unchecked or Qt.Checked
        """
        if state == Qt.Unchecked:
            self.settings.general.enable_splashscreen = False
        elif state == Qt.Checked:
            self.settings.general.enable_splashscreen = True

    def __init__(self, window, settings, *args, **kwargs):
        super(GeneralTab, self).__init__(*args, **kwargs)

        self.win = window
        self.settings = settings

        # Create inputs for each general option.
        self.websiteFileField = QLineEdit()
        self.websiteFileField.textChanged.connect(self.websiteFileFieldChanged)

        # The index of each launch option should correspond to the correct LaunchMode.
        self.launchOpt = QComboBox()
        self.launchOpt.addItems(["Webiste", "Open file", "Restore last session"])
        self.launchOpt.currentIndexChanged.connect(self.launchModeValueChanged)

        self.intervalSpinner = QSpinBox()
        self.intervalSpinner.setMinimum(0)
        self.intervalSpinner.valueChanged.connect(self.saveIntervalValueChanged)

        self.splashScreenCheckBox = QCheckBox()
        self.splashScreenCheckBox.stateChanged.connect(self.enableSplashScreenStateChanged)

        splashScreenContainer = QWidget()
        splashScreenLayout = QHBoxLayout(splashScreenContainer)
        margin = splashScreenLayout.contentsMargins()
        splashScreenLayout.setContentsMargins(0, margin.top(), 0, 0)
        splashScreenLayout.setAlignment(Qt.AlignLeft)
        splashScreenLayout.addWidget(self.splashScreenCheckBox)

        label = QLabel("Enable splash screen")
        label.setToolTip("When the splash screen is disabled, it is not possible to interrupt the startup anymore.")
        splashScreenLayout.addWidget(label)

        # Add all elements to the tab.
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QLabel("Launch mode:"))
        layout.addWidget(self.launchOpt)

        self.websiteFileLabel = QLabel("Website URL:")
        layout.addWidget(self.websiteFileLabel)
        layout.addWidget(self.websiteFileField)

        label = QLabel("Save interval:")
        label.setToolTip("Save the application each n seconds. Choose 0 to disable saving.")
        layout.addWidget(label)
        layout.addWidget(self.intervalSpinner)

        layout.addWidget(splashScreenContainer)

        # Fill all the text fields.
        self.loadSettings()

    def loadSettings(self):
        """
        Fill the ui with the stored values.
        :param settings: all settings stored as dictionary
        """
        # Update the splashscreen option.
        splashscreen_enabled = self.settings.general.enable_splashscreen
        self.splashScreenCheckBox.setCheckState(Qt.Checked if splashscreen_enabled else Qt.Unchecked)

        # Update the save interval stepper.
        self.intervalSpinner.setValue(self.settings.general.save_interval)

        # Select the launch mode in the combo box and update the corresponding text field.
        launch_mode = self.settings.general.launch_mode
        self.launchOpt.setCurrentIndex(launch_mode)
        self.launchModeValueChanged(launch_mode)

class HeaderTab(QWidget):
    
    def spinnerValueChanged(self):
        """
        Callback when one of the spinner values changes.
        """
        low = self.lowerSpinner.value()
        high = self.upperSpinner.value()
        self.upperSpinner.setMinimum(low)
        self.lowerSpinner.setMaximum(high)

        # Update the settings.
        self.settings.header.point_indices = range(low, high)

    def nameFieldChanged(self, text):
        """
        Called when the name field value changes.
        :param text: new entered text
        """
        self.settings.header.name_field = text

    def sumFieldChanged(self, text):
        """
        Called when the sum field value changes.
        :param text: new entered text
        """
        self.settings.header.sum_field = text

    def loadSettings(self):
        """
        Fill the ui with the stored values.
        :param settings: all settings stored as dictionary
        """
        # Update the text fields.
        self.nameField.setText(self.settings.header.name_field)
        self.sumField.setText(self.settings.header.sum_field)

        # Update the Spinner to only allow valid values.
        point_fields_range = self.settings.header.point_indices
        self.upperSpinner.setValue(point_fields_range.stop)
        self.lowerSpinner.setValue(point_fields_range.start)
        self.spinnerValueChanged()

    def __init__(self, window, settings, *args, **kwargs):
        super(HeaderTab, self).__init__(*args, **kwargs)

        self.win = window
        self.settings = settings

        # Name of name and sum fields.
        self.nameField = QLineEdit()
        self.nameField.textChanged.connect(self.nameFieldChanged)

        self.sumField = QLineEdit()
        self.sumField.textChanged.connect(self.sumFieldChanged)

        # Create spinner to configure point fields.
        self.lowerSpinner = QSpinBox()
        self.lowerSpinner.valueChanged.connect(self.spinnerValueChanged)

        self.upperSpinner = QSpinBox()
        self.upperSpinner.valueChanged.connect(self.spinnerValueChanged)

        spinnerContainer = QWidget()
        spinnerLayout = QHBoxLayout(spinnerContainer)
        spinnerLayout.setAlignment(Qt.AlignLeft)
        spinnerLayout.setContentsMargins(0, 0, 0, 0)

        spinnerLayout.addWidget(QLabel("Start:"))
        spinnerLayout.addWidget(self.lowerSpinner)
        spinnerLayout.addWidget(QLabel("End:"))
        spinnerLayout.addWidget(self.upperSpinner)

        # Add all elements to the layout.
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(QLabel("Name field:"))
        layout.addWidget(self.nameField)
        layout.addWidget(QLabel("Sum field:"))
        layout.addWidget(self.sumField)
        layout.addWidget(QLabel("Point fields:"))
        layout.addWidget(spinnerContainer)

        self.loadSettings()


class MonoidPreferencesWindow(QDialog):
    """
    Applications Preferences window.
    """
    def __init__(self, app, *args, **kwargs):
        super(MonoidPreferencesWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Settings")
        self.app = app

        # Place the tab widget inside layout to get some margin.
        self.tabs = QTabWidget(self)
        self.tabs.currentChanged.connect(self.updateHeight)

        layout = QVBoxLayout(self);
        layout.addWidget(self.tabs)

        # Create each tab.
        self.generalTab = GeneralTab(self, app.settings)
        self.headerTab = HeaderTab(self, app.settings)

        # Add all the tabs.
        self.tabs.addTab(self.generalTab, "General")
        self.tabs.addTab(self.headerTab, "Header")

    def show(self, *args):
        """
        Set the size to a fixed one after showing the window to disable the minimize and maximize button.
        """
        super(MonoidPreferencesWindow, self).show(*args)
        self.setFixedSize(self.minimumSizeHint())

    def updateHeight(self, index):
        """
        Set the window height to the minimum required space.
        :param index: index of the currently selected tab
        """
        # Resize all tabs.
        for i in range(self.tabs.count()):
            if i != index:
                widget = self.tabs.widget(i)
                widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
                widget.resize(widget.sizeHint())
                widget.adjustSize()

        widget = self.tabs.widget(index)
        if widget:
            widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            widget.resize(widget.minimumSizeHint())
            widget.adjustSize()

            # Resize the tab widget.
            self.tabs.resize(self.tabs.minimumSizeHint())
            self.tabs.adjustSize()

            # Resize the window to the fixed minimum size.
            self.setFixedSize(self.minimumSizeHint())
            self.adjustSize()
