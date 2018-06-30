# -*- coding: utf-8 -*-

from __future__ import absolute_import

import argparse
import subprocess
import os
import errno
import getpass
import re
import codecs
import shutil
import platform
"""Utils prepared for makefile

    This module will include:
        sphinx
        offline distribution
        ...

    Example:
        None

    Attributes:
        module_level_variable (int): description

"""

here = os.path.abspath(os.path.dirname(__file__))

# folder

DOC_FOLDER = 'docs'
HTML_FOLDER = os.path.join(DOC_FOLDER, 'html')

DEP_FOLDER = 'deps'
MAC_DEP_FOLDER = os.path.join(DEP_FOLDER, 'macosx')
LINUX_DEP_FOLDER = os.path.join(DEP_FOLDER, 'linux')

SRC_FOLDER = 'src'
PROJECT_NAME = 'secret_miner'

WORK_DIR_ABPATH = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

os.chdir(WORK_DIR_ABPATH)

# system

CURRENT_SYSTEM = platform.system()


def mkdir_exist(directory):
    """TODO: Docstring for mkdir_exist.

    Args:
        directory (str): TODO

    """
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


class Editor(object):
    """an editor used regex to replace certain lines """

    def __init__(self, fpath):
        """TODO: to be defined1. """
        self._fpath = fpath
        self._swp_lines = []

        # unit test mock doesn't support `for line in f`
        with open(fpath) as f:
            self._swp_lines = [s.rstrip() for s in f.read().splitlines()]

    @property
    def fpath(self):
        return self._fpath

    def editline_with_regex(self, regex_tgtline, to_replace):
        """find the first matched line, then replace

        Args:
            regex_tgtline (str): regular expression used to match the target line
            to_replace    (str): line you wanna use to replace

        """
        for idx, line in enumerate(self._swp_lines):
            mobj = re.match(regex_tgtline, line)

            if mobj:
                self._swp_lines[idx] = to_replace

                return

    def finish_writing(self):
        content = list(map(lambda x: x + '\n', self._swp_lines))

        with open(self.fpath, 'w') as f:
            f.write(''.join(content))


class ProjectInfo(object):
    """Common information for the project"""

    def __init__(self, **kwinfo):
        """init project info

        Args:
            author_fakename (str): TODO
            author_truename (str): TODO
            email (str): TODO
            project_name (str): TODO
            project_version (str): TODO


        """
        self._author_fakename = getpass.getuser()
        self._author_truename = ProjectInfo.find_pakcage_info(
            'author', SRC_FOLDER, PROJECT_NAME, '__init__.py')
        self._email = ProjectInfo.find_pakcage_info(
            'email', SRC_FOLDER, PROJECT_NAME, '__init__.py')
        self._project_name = os.path.basename(
            os.path.dirname(os.path.realpath(__file__)))
        self._project_version = ProjectInfo.find_pakcage_info(
            'version', SRC_FOLDER, PROJECT_NAME, '__init__.py')

        for key, info in kwinfo.items():
            key = '_' + key
            setattr(self, key, info)

    @property
    def author_fakename(self):
        return self._author_fakename

    @property
    def author_truename(self):
        return self._author_truename

    @property
    def email(self):
        return self._email

    @property
    def project_name(self):
        return self._project_name

    @property
    def project_version(self):
        return self._project_version

    @classmethod
    def _read(cls, *parts):
        with codecs.open(os.path.join(here, *parts), 'r') as fp:
            return fp.read()

    @classmethod
    def find_pakcage_info(cls, info, *file_paths):
        info_file = ProjectInfo._read(*file_paths)

        match = re.search(
            r"^__" + re.escape(info) + r"__ = ['\"]([^'\"]*)['\"]", info_file,
            re.M)

        if match:
            return match.group(1)
        raise RuntimeError("Unable to find {} string.".format(info))


proj_info = ProjectInfo()
author_fakename = proj_info.author_fakename
author_truename = proj_info.author_truename
email = proj_info.email
project_name = proj_info.project_name
project_version = proj_info.project_version

########################################################################################################################
#                                                      exceptions                                                      #
########################################################################################################################


class PJUtilsError(Exception):
    """Base pjutils exception"""


class PlatformNotSupportedError(PJUtilsError):
    """General exception in PyOfflineDist"""


class PythonVersionNotSupportedError(PJUtilsError):
    """General exception in PyOfflineDist"""


########################################################################################################################
#                                                        sphinx                                                        #
########################################################################################################################


class Sphinx(object):
    """Docstring for Sphinx. """

    def __init__(self, proj_info):
        """TODO: to be defined1.

        Args:
            proj_info (ProjectInfo): TODO


        """
        self._proj_info = proj_info
        self.__docfolder = DOC_FOLDER
        self.__htmlfolder = HTML_FOLDER

        self.conf_fpath = os.path.abspath(
            os.path.join(self.__docfolder, 'conf.py'))
        self.code_fdpath = os.path.abspath(
            os.path.join(SRC_FOLDER, self.proj_info.project_name))

        self._sphinx_quickstart_cmd = [
            'sphinx-quickstart', self.__docfolder, '-p',
            self.proj_info.project_name, '-a', self.proj_info.author_fakename,
            '-v', self.proj_info.project_version, '-r',
            self.proj_info.project_version, '-l', 'en', '--ext-autodoc',
            '--makefile', '--quiet'
        ]
        self._sphinx_apidoc_cmd = [
            'sphinx-apidoc', self.code_fdpath, '-o', self.__docfolder, '-M',
            '--force'
        ]

        # sphinx-build -b html docs html
        self._sphinx_buildhtml_cmd = [
            'sphinx-build', '-b', 'html', self.__docfolder, self.__htmlfolder
        ]

        # make sure directories exist
        mkdir_exist(self.__docfolder)
        mkdir_exist(self.__htmlfolder)

    @property
    def proj_info(self):
        return self._proj_info

    @property
    def sphinx_quickstart_cmd(self):
        return self._sphinx_quickstart_cmd

    def quickstart(self):
        """TODO: Docstring for quickstart.  """
        subprocess.call(self.sphinx_quickstart_cmd)

        pass

    def gen_code_api(self):
        """TODO: Docstring for gen_code_api."""

        # edit config file

        conf_editor = Editor(self.conf_fpath)

        # insert code path for searching
        conf_editor.editline_with_regex(r'^# import os', 'import os')
        conf_editor.editline_with_regex(r'^# import sys', 'import sys')
        conf_editor.editline_with_regex(
            r'^# sys\.path\.insert',
            'sys.path.insert(0, "{}")'.format(self.code_fdpath))
        conf_editor.editline_with_regex(
            r"""html_theme = 'alabaster'""",
            'html_theme = \'default\''.format(self.code_fdpath))

        conf_editor.finish_writing()

        # sphinx-apidoc to generate rst from source code

        # force regenerate
        subprocess.call(self._sphinx_apidoc_cmd)

        pass

    def rst2html(self):
        subprocess.call(self._sphinx_buildhtml_cmd)
        pass


########################################################################################################################
#                                                 offline distribution                                                 #
########################################################################################################################


class PyOfflineDist(object):
    """offline distribution for python project"""

    def __init__(self, req_fpath='requirements.txt'):
        """TODO: to be defined1. """
        self.__dep_folder = DEP_FOLDER
        self.__req_fpath = req_fpath

        self._srcpj_abfdpath = os.path.abspath(
            os.path.join(SRC_FOLDER, PROJECT_NAME))

        pass

    def freeze_deps(self):
        with open(self.__req_fpath, 'w') as f:
            self._freeze_deps_cmd = ['pip', 'freeze']
            p = subprocess.Popen(self._freeze_deps_cmd, stdout=f)
            p.wait()
        pass

    def __get_dep_folder(self):
        if CURRENT_SYSTEM == 'Darwin':
            self.__dep_folder = os.path.join(DEP_FOLDER, 'macosx')
        elif CURRENT_SYSTEM == 'Linux':
            self.__dep_folder = os.path.join(DEP_FOLDER, 'linux')
        else:
            raise PlatformNotSupportedError('only support for mac or linux')

    def download_deps(self):
        self.__get_dep_folder()

        mkdir_exist(self.__dep_folder)

        self._download_deps_cmd = [
            'pip', 'download', '-r', self.__req_fpath, '-d', self.__dep_folder
        ]
        subprocess.call(self._download_deps_cmd)

    def install_deps(self):
        self.__get_dep_folder()

        self._install_deps_cmd = [
            'pip', 'install', '--no-index', '--find-links', self.__dep_folder,
            '-r', self.__req_fpath
        ]
        subprocess.call(self._install_deps_cmd)

    def clean_deps(self):
        self.__get_dep_folder()

        shutil.rmtree(self.__dep_folder, ignore_errors=True)

    def pyinstaller_mkbinary(self, script_name):
        self._pyinstaller_mkbinary_cmd = [
            'pyinstaller', '--onefile', script_name
        ]

        # enter the source code directory
        os.chdir(self._srcpj_abfdpath)

        # execute pyinstaller
        # generate dist and build folders
        subprocess.call(self._pyinstaller_mkbinary_cmd)

        # return to previous directory
        os.chdir(WORK_DIR_ABPATH)

        pass

    def clean_binary(self):
        # enter the source code directory
        os.chdir(self._srcpj_abfdpath)

        shutil.rmtree('dist', ignore_errors=True)
        shutil.rmtree('build', ignore_errors=True)

        # return to previous directory
        os.chdir(WORK_DIR_ABPATH)
        pass


########################################################################################################################
#                                                      Commandline Interface                                                       #
########################################################################################################################


def add_subcommands(subparsers):
    # sphinx

    parser_sphinx = subparsers.add_parser('sphinx', help='sphinx help')

    parser_sphinx.add_argument('--quickstart', action='store_true')
    parser_sphinx.add_argument('--gen-code-api', action='store_true')
    parser_sphinx.add_argument('--rst2html', action='store_true')

    # offline_dist

    parser_offline_dist = subparsers.add_parser(
        'offline_dist', help='offline_dist help')

    parser_offline_dist.add_argument('--freeze-deps', action='store_true')
    parser_offline_dist.add_argument('--download-deps', action='store_true')
    parser_offline_dist.add_argument('--install-deps', action='store_true')
    parser_offline_dist.add_argument('--clean-deps', action='store_true')
    parser_offline_dist.add_argument('--mkbinary')
    parser_offline_dist.add_argument('--clean-binary', action='store_true')

    #  subparsers_offline_dist = parser_offline_dist.add_subparsers(dest='offline_dist_command')
    #
    #  parser_download = subparsers_offline_dist.add_parser('download')
    #  parser_install = subparsers_offline_dist.add_parser('install')
    #  parser_mkbinary = subparsers_offline_dist.add_parser('mkbinary')

    # download
    #  parser_download.add_argument('--platform', action='store', choices=['macosx-10_10_x86_64', 'linux_x86_64'])
    #  parser_download.add_argument('--python-version', action='store', choices=['27', '3'])

    # install

    # mkbinary

    pass


def execute_by_options(args):
    """execute by argument dictionary

    Args:
        args (dict): command line argument dictionary

    """
    if args['subcommand'] == 'sphinx':
        s = Sphinx(proj_info)
        if args['quickstart']:
            s.quickstart()
        elif args['gen_code_api']:
            s.gen_code_api()
        elif args['rst2html']:
            s.rst2html()
        pass
    elif args['subcommand'] == 'offline_dist':
        pod = PyOfflineDist()
        if args['freeze_deps']:
            pod.freeze_deps()
        elif args['download_deps']:
            pod.download_deps()
        elif args['install_deps']:
            pod.install_deps()
        elif args['clean_deps']:
            pod.clean_deps()
        elif args['mkbinary']:
            pod.pyinstaller_mkbinary(args['mkbinary'])
        elif args['clean_binary']:
            pod.clean_binary()

    pass


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(
        help='sub-command help', dest='subcommand')

    add_subcommands(subparsers)

    args = vars(parser.parse_args())

    execute_by_options(args)

    #  if args['sphinx'] ==


if __name__ == '__main__':
    main()
