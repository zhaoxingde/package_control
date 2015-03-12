import sublime
import sys
import os

# These imports are used during the sanity checking phase
try:
    # Python 3
    from .package_control import text, sys_path
except (ValueError):
    # Python 2
    from package_control import text, sys_path


st_version = 2

# Warn about out-dated versions of ST3
if sublime.version() == '':
    st_version = 3
    print('Package Control: Please upgrade to Sublime Text 3 build 3012 or newer')

elif int(sublime.version()) > 3000:
    st_version = 3


if st_version == 3:
    installed_dir, _ = __name__.split('.')

    package_path = os.path.join(sys_path.st_dir, 'Installed Packages', 'Package Control.sublime-package')
    pc_python_path = os.path.join(sys_path.st_dir, 'Packages', 'Package Control', 'Package Control.py')
    has_packed = os.path.exists(package_path)
    has_unpacked = os.path.exists(pc_python_path)

elif st_version == 2:
    installed_dir = os.path.basename(os.getcwd())


# Ensure the user has installed Package Control properly
if installed_dir != 'Package Control':
    message = text.format(
        u'''
        Package Control

        This package appears to be installed incorrectly.

        It should be installed as "Package Control", but seems to be installed
        as "%s".

        To fix the issue, please:

        1. Open the "Preferences" menu
        2. Select "Browse Packages\u2026"
        ''',
        installed_dir,
        strip=False
    )

    # If installed unpacked
    if os.path.exists(os.path.join(sys_path.st_dir, 'Packages', installed_dir)):
        message += text.format(
            u'''
            3. Rename the folder "%s" to "Package Control"
            4. Restart Sublime Text
            ''',
            installed_dir
        )
    # If installed as a .sublime-package file
    else:
        message += text.format(
            u'''
            3. Browse up a folder
            4. Browse into the "Installed Packages/" folder
            5. Rename "%s.sublime-package" to "Package Control.sublime-package"
            6. Restart Sublime Text
            ''',
            installed_dir
        )
    sublime.error_message(message)

elif st_version == 3 and has_packed and has_unpacked:
    message = text.format(
        u'''
        Package Control

        It appears you have Package Control installed as both a
        .sublime-package file and a directory inside of the Packages folder.

        To fix this issue, please:

        1. Open the "Preferences" menu
        2. Select "Browse Packages\u2026"
        3. Delete the folder "Package Control"
        4. Restart Sublime Text
        '''
    )
    sublime.error_message(message)

# Normal execution will finish setting up the package
else:
    reloader_name = 'package_control.reloader'

    # ST3 loads each package as a module, so it needs an extra prefix
    if st_version == 3:
        reloader_name = 'Package Control.' + reloader_name
        from imp import reload

    # Make sure all dependencies are reloaded on upgrade
    if reloader_name in sys.modules:
        reload(sys.modules[reloader_name])

    try:
        # Python 3
        from .package_control.commands import *
        from .package_control.package_cleanup import PackageCleanup

    except (ValueError):
        # Python 2
        from package_control.commands import *
        from package_control.package_cleanup import PackageCleanup

    def plugin_loaded():
        # Make sure the user's locale can handle non-ASCII. A whole bunch of
        # work was done to try and make Package Control work even if the locale
        # was poorly set, by manually encoding all file paths, but it ended up
        # being a fool's errand since the package loading code built into
        # Sublime Text is not written to work that way, and although packages
        # could be installed, they could not be loaded properly.
        try:
            os.path.exists(os.path.join(sublime.packages_path(), u"fran\u00e7ais"))
        except (UnicodeEncodeError):
            message = text.format(
                u'''
                Package Control

                Your system's locale is set to a value that can not handle
                non-ASCII characters. Package Control can not properly work
                unless this is fixed.

                On Linux, please reference your distribution's docs for
                information on properly setting the LANG environmental variable.
                As a temporary work-around, you can launch Sublime Text from the
                terminal with:

                LANG=en_US.UTF-8 sublime_text
                '''
            )
            sublime.error_message(message)
            return

        # Start shortly after Sublime starts so package renames don't cause errors
        # with keybindings, settings, etc disappearing in the middle of parsing
        sublime.set_timeout(lambda: PackageCleanup().start(), 2000)

    if st_version == 2:
        plugin_loaded()
