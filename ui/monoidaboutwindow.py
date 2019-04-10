from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap


class MonoidAboutWindow(QDialog):
    """
    Applications About window. At the moment this window just displays the Monoid logo, without any additional
    informtion.
    """

    def __init__(self, app, *args, **kwargs):
        super(MonoidAboutWindow, self).__init__(*args, **kwargs)

        # Load required data for about window.
        self.logo = QPixmap("images/logo.png")
        self.app = app

        # Configure window.
        self.setWindowTitle("About {0}".format(app.applicationName()))

        # Add logo and app name labels.
        self.logo_view = QLabel(self)
        self.logo_view.setPixmap(self.logo)
        self.logo_view.setToolTip("I love you!")

    def show(self, *args):
        """
        Set the size to a fixed one after showing the window to disable the minimize and maximize button.
        """
        super(MonoidAboutWindow, self).show(*args)
        self.setFixedSize(self.logo.size())
