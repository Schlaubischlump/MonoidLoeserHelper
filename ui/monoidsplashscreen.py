from time import time
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor, QPainter
from PyQt5.QtWidgets import QSplashScreen, QLabel, QProgressBar

class MonoidSplashScreen(QSplashScreen):
    """
    Splash screen which displays the Monoid logo and a progressbar. Currently this progressbar is shown for one second,
    without doing anything meaningful in the background (See: animateFakeProgress). This splash screen just exists to
    give the user some time to interrupt the startup process by pressing a specific modifier key.
    """

    def __init__(self, app, footerText=""):
        self.app = app
        self._modifierKey = None
        self._callback = None

        # Create and display the splash screen.
        splashBg = QPixmap("images/logo_background.png")
        h, w = splashBg.height(), splashBg.width()

        # Leave some extra space for the footer text.
        padding_bottom = 20

        # Draw a solid white background for the logo.
        bg = QPixmap(w, h + padding_bottom)
        p = QPainter(bg)
        p.fillRect(0, 0, bg.width(), bg.height(), QColor(255, 255, 255, 255));
        p.end()

        # Create SplashScreen instance.
        super(MonoidSplashScreen, self).__init__(bg, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        # Add Monoid logo background.
        background = QLabel(self)
        background.setPixmap(splashBg)

        # Add progress bar. (0.66 is the percentage of the distance from the top of the logo to the red dots)
        self.progressBar = QProgressBar(self)
        self.progressBar.setStyleSheet("QProgressBar::chunk{background-color: red;}")
        self.progressBar.setGeometry(0, h * 0.66, w, 2)

        # Add Monoid logo foreground.
        splashFg = QPixmap("images/logo_foreground.png")
        foreground = QLabel(self)
        foreground.setPixmap(splashFg)

        # Add footer text.
        self.showMessage("<font color='black'>{0}</font>".format(footerText), Qt.AlignBottom | Qt.AlignCenter, Qt.black)

    def mousePressEvent(self, event):
        """
        Override event to prevent dismissing the SplashScreen with a mouse click.
        :param event: received event
        """
        pass

    def startupInterruptionModifierKey(self):
        """
        :return the current modifier key to dismiss the splashscreen
        """
        return self._modifierKey

    def setStartupInterruptionModifierKey(self, key, callback):
        """
        Interrupt the startup and hide the splashscreen by pressing this key.
        :param key: modifier key (Qt.ShiftModifier, Qt.ControlModifier, Qt.AltModifier, Qt.MetaModifier)
        :param callback: callback function to call after key is pressed
        """
        assert(key in [Qt.ShiftModifier, Qt.AltModifier, Qt.MetaModifier, Qt.ControlModifier])

        self._modifierKey = key
        self._callback = callback

    def animateFakeProgress(self):
        """
        Animate the progress bar. We aren't doing anything here.
        This method just exists to give the user some time to interrrupt the startup by holding down shift.
        """
        self.progressBar.setMaximum(10)

        for i in range(1, self.progressBar.maximum()+1):
            self.progressBar.setValue(i)
            t = time()
            while time() < t + 0.1:
                # Dismiss the splashscreen when modifer key is pressed.
                if self._modifierKey and self.app.queryKeyboardModifiers() == self._modifierKey:
                    self.hide()
                    self._callback()
                    return
                self.app.processEvents()
