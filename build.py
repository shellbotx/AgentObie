# This will create a dist directory containing the executable file, all the data
# directories. All Libraries will be bundled in executable file.
#
# Run the build process by entering 'pygame2exe.py' or
# 'python pygame2exe.py' in a console prompt.
#
# To build exe, python, pygame, and py2exe have to be installed. After
# building exe none of this libraries are needed.
#
# Please Note have a backup file in a different directory as if it crashes you
# will loose it all!(I lost 6 months of work because I did not do this)

try:
    from distutils.core import setup
    import py2exe
    import pygame
    from modulefinder import Module
    import glob
    import fnmatch
    import sys
    import os
    import shutil
    import operator
except ImportError as message:
    raise SystemExit("Unable to load module. %s" % message)

# Hack which fixes pygame mixer and pygame font

# save the original before we edit it
orig_is_system_DLL = py2exe.build_exe.isSystemDLL


def is_system_DLL(pathname):
    # checks if the freetype and ogg dll files are being included
    if os.path.basename(pathname).lower() in ("libfreetype-6.dll", "libogg-0.dll", "sdl_ttf.dll"):
        return 0
    return orig_is_system_DLL(pathname)  # return original function


py2exe.build_exe.isSystemDLL = is_system_DLL  # override default function


class pygame2exe(py2exe.build_exe.py2exe):
    # This hack makes sure that pygame default font is copied: no need to modify code for specifying default font
    def copy_extensions(self, extensions):
        # Get pygame default font
        pygame_dir = os.path.split(pygame.base.__file__)[0]
        pygame_default_font = os.path.join(pygame_dir, pygame.font.get_default_font())

        # Add font to list of extensions to be copied
        extensions.append(Module("pygame.font", pygame_default_font))
        py2exe.build_exe.py2exe.copy_extensions(self, extensions)


class BuildExe:
    def __init__(self):
        # Name of starting .py
        self.script = "main.py"

        # Name of program
        self.project_name = "Agent Obie"

        # Project url
        self.project_url = "about:none"

        # Version of program
        self.project_version = "0.4"

        # License of program
        self.license = ""

        # Author of program
        self.author_name = "shellbot"
        self.author_email = "shellbot@studioshellbot.com"
        self.copyright = "Copyright (c) 2015 shellbot"

        # Description
        self.project_description = "Agent Obie alpha build v4"

        # Icon file (if None will use pygame default icon)
        self.icon_file = None

        # Extra files / dirs copied to game
        self.extra_datas = ['assets', 'assets/img', 'assets/stage']

        # Extra / exclude python modules
        self.extra_modules = []
        self.exclude_modules = []

        # DLL Excludes
        self.exclude_dll = ['']

        # Python scripts (strings) to be included, seperated by a comma
        self.extra_scripts = []

        # Zip file name (None will bundle files in exe instead of zip file)
        self.zipfile_name = None

        # Dist directory
        self.dist_dir = 'dist'

    # Code from DistUtils tut @ http://wiki.python.org/main/DistUtils/Tutorial
    # Originally borrowed from wxPython's setup and config files
    def opj(self, *args):
        path = os.path.join(*args)
        return os.path.normpath(path)

    def find_data_files(self, srcdir, *wildcards, **kw):
        # get a list of all files under the srcdir matching wildcards
        # returned in a format to be used for install_data
        def walk_helper(arg, dirname, files):
            if '.svn' in dirname:
                return
            names = []
            lst, wildcards = arg
            for wc in wildcards:
                wc_name = self.opj(dirname, wc)
                for f in files:
                    filename = self.opj(dirname, f)

                    if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
                        names.append(filename)
            if names:
                lst.append((dirname, names))

        file_list = []
        recursive = kw.get('recursive', True)
        if recursive:
            os.path.walk(srcdir, walk_helper, (file_list, wildcards))
        else:
            walk_helper((file_list, wildcards), srcdir, [os.path.basename(f) for f in glob.glob(self.opj(srcdir, '*'))])
        return file_list

    def run(self):
        # Erase previous destination dir
        if os.path.isdir(self.dist_dir):
            shutil.rmtree(self.dist_dir)

        # Use the default pygame icon, if none given
        if self.icon_file is None:
            path = os.path.split(pygame.__file__)[0]
            self.icon_file = os.path.join(path, 'pygame.ico')

        # List all data files to add
        extra_datas = []
        for data in self.extra_datas:
            if os.path.isdir(data):
                extra_datas.extend(self.find_data_files(data, '*'))
            else:
                extra_datas.extend(('.', [data]))

        setup(
            cmdclass={'py2exe': pygame2exe},
            version=self.project_version,
            description=self.project_description,
            name=self.project_name,
            url=self.project_url,
            author=self.author_name,
            author_email=self.author_email,
            license=self.license,

            # Targets to build
            windows=[{
                'script': self.script,
                'icon_resources': [(0, self.icon_file)],
                'copyright': self.copyright
            }],
            options={
                'py2exe': {
                    'optimize': 2,
                    'bundle_files': 1,
                    'compressed': True,
                    'excludes': self.exclude_modules,
                    'packages': self.extra_modules,
                    'dll_excludes': self.exclude_dll,
                    'includes': self.extra_scripts
                }
            },
            zipfile=self.zipfile_name,
            data_files=extra_datas,
            dist_dir=self.dist_dir
        )

        # Clean up build dir
        if os.path.isdir('build'):
            shutil.rmtree('build')


if __name__ == '__main__':
    if operator.lt(len(sys.argv), 2):
        sys.argv.append('py2exe')
    BuildExe().run()  # Run generation
    input("Press 'ENTER' to exit")  #
