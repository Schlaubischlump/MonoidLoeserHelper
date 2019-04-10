"""
There are a couple of assumptions necessary to make this program work.
1. The url of the monoid website must not change (see Settings: Website URL)
2. The html layout of the monoid website must not change. (see: parser.py and rewrite it)
3. The name and sum title in the table on the website must not change (see Settings: Name field, Sum field)
4. The index of the point fields for each release should be at position 4-7 [Meaning the i-th to j-th heading inside the
   table] (see Settings: Point fields)

Coding conventions:
- When writing methods related to qt classes use camelCase (to stay consistent with the API), otherwise use snake_case.
"""

import sys
import argparse
from functools import partial

from PyQt5.QtCore import QTimer, QObject, Qt
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence

from ui import MonoidApp, MonoidSplashScreen, OptionDialog
from util.parser import fetch_latest_data, parse_website_data, parse_php_file
from util.config import LaunchMode, TEMPLATE_FILE



def prepare_app_launch(app, launch_mode, path=""):
    """
    Load the necessary data to launch the application.
    :param app: main QApplication
    :param launch_mode: See the LaunchMode enum
    :param path: path to the file to open for LaunchMode.FILE
    :return True if the required data could be loaded, False otherwise.
    """
    # True if the data could be loaded, otherwise False. False indicated, that the fallback to the default template
    # file should be executed. The window is only displayed if this flag is True.
    did_load = False

    # Try to load the last known application state.
    if launch_mode == LaunchMode.RESTORE:
        did_load = app.restoreApplicationState()

    # Try to load the latest data from the website
    elif launch_mode == LaunchMode.WEBSITE:
        # Try to fetch the latest website data.
        url = app.settings.general.website_url
        try:
            data = fetch_latest_data(url)
        except:
            app.showError("Error retrieving data!", "Error fetching the latest data. Please make sure that the "\
                          "monoid website is online, you are connected to the internet and that the url: '{0}' "\
                          "is still valid.".format(url))
        else:
            # Try to parse the website data if it could be fetched.
            try:
                headers, users = parse_website_data(data)
                app.setData(headers, users)
                did_load = True
            except:
                app.showError("Parse error!", "Error parsing the website data. Please make sure that the monoid "\
                              "website layout has not changed.")

    # Try to parse a specific user requested file.
    elif launch_mode == LaunchMode.FILE and path:
        try:
            headers, users = parse_php_file(path)
            app.setData(headers, users)
            did_load = True
        except:
            app.showError("Corrupt file.", "Error parsing the file: {0}. Make sure the file is a "\
                          "valid php file.".format(path))

    # Parse the default template file if requested or if fetching the webiste failed.
    if launch_mode == LaunchMode.TEMPLATE or not did_load:
        try:
            headers, users = parse_php_file(TEMPLATE_FILE)
            app.setData(headers, users)
            did_load = True
        except:
            app.showError("Corrupt template file.", "Error parsing the template file. Make sure the file is a "\
                          "valid php file.")

    return did_load


def present_startup_option_menu(app, args):
    """
    Interrupt the application startup to show different options. This function has no return value, but modifies the
    args data structure to represent the selected options.
    :param app: main application
    :param args: application startup arguments
    """
    # When this Dialog is dismissed, the program flow will return to prepare_app_launch.
    options = OptionDialog("Options", options=["Load from Website",
                                               "Load empty template",
                                               "Restore last application state",
                                               "Delete last application state"])
    res = options.exec_()

    if res == OptionDialog.Accepted:
        # Get the user selected option.
        opt = options.getOption()
        # Reset all arguments and set only the selected one.
        args.open_file=None
        args.website = (opt == 0)
        args.template = (opt == 1)
        args.restore_state = (opt == 2)
        args.delete_app_state = (opt == 3)
    else:
        sys.exit()


if __name__ == "__main__":
    # Configure the command line options.
    parser = argparse.ArgumentParser(description="Launch configuration for the MonoidApp.")
    parser.add_argument("-w", "--website", action="store_true", help="Fetch the latest data from the Monoid website. "\
                        "This is the default launch option.")
    parser.add_argument("-t", "--template", action="store_true", help="Open the default template file. "\
                        "This is the fallback option if the specified option fails.")
    parser.add_argument("-r", "--restore-state", action="store_true", help="Restore the last known application state.")
    parser.add_argument("-o", "--open-file", type=str, help="Open a specific php file at launch.")
    parser.add_argument("-s", "--save-app-state", type=int, help="Save the application state every s seconds. "\
                        "Use -1 to disable saving the application state.", default=None)
    parser.add_argument("-d", "--delete-app-state", action="store_true", help = "Delete the currently save application"\
                        " state.")
    parser.add_argument("-p", "--skip-splashscreen", action="store_true", help="Skip the application splash screen. "\
                        "You wont be able to show the start menu when the splashscreen is disabled.", default=None)
    args = parser.parse_args()


    # Create the main application.
    app = MonoidApp(sys.argv)

    # Show a Splashscreen with a fake progressbar to allow interrupting the startup.
    if args.skip_splashscreen is None:
        args.skip_splashscreen = not app.settings.general.enable_splashscreen

    if not args.skip_splashscreen:
        splash = MonoidSplashScreen(app, footerText="Press Shift to interrupt startup...")
        splash.setStartupInterruptionModifierKey(Qt.ShiftModifier, partial(present_startup_option_menu, app, args))
        splash.show()
        splash.animateFakeProgress()

    # Determine how the app should be launched.
    path = ""
    launch_mode = LaunchMode.WEBSITE

    if args.website:
        pass
    elif args.restore_state:
        launch_mode = LaunchMode.RESTORE
    elif args.template:
        launch_mode = LaunchMode.TEMPLATE
    elif args.open_file:
        launch_mode = LaunchMode.FILE
        path = args.open_file
    else:
        # Choose the settings from the settings file.
        launch_mode = LaunchMode(app.settings.general.launch_mode)
        path = app.settings.general.file_path

    # Delete the application state if requested.
    if args.delete_app_state:
        app.deleteApplicationState()

    # Start the main application
    did_load = prepare_app_launch(app, launch_mode, path)

    # Show UI and run the App.
    if did_load:
        # Repeatly schedule a timer to save the current application state.
        if args.save_app_state is None:
            interval = app.settings.general.save_interval
        else:
            interval = args.save_app_state

        if interval > 0:
            timer = QTimer()
            timer.timeout.connect(app.saveApplicationState)
            timer.start(interval*1000)

        # Show the main Application window.
        app.showWindow()

        # Dismiss the Splashscreen with a nice fading animation.
        if not args.skip_splashscreen:
            splash.finish(app.win)

        ret = app.exec_()
        # Save the application state when the app quits.
        if interval > 0:
            app.saveApplicationState()

        # Save application settings.
        app.saveSettings()

        # Exit the application.
        sys.exit(ret)
