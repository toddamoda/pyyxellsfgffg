"""TBW."""

import subprocess
import os
import time


class ViewerException(Exception):
    """Base class for all exceptions raised in the :module:`viewer.py` module."""


class DS9Exception(ViewerException):
    """Base class for all exceptions raised in the :class:`DS9` class."""


class DS9(object):
    """This class remotely controls a DS9 application remotely using the XPA interface.

    On Debian based machines you need to install the proper tools,

    * apt install saods9
    * apt install xpa-tools

    These are installed into the /usr/bin directory.
    """

    def __init__(self, ds9_exe='/usr/bin/ds9'):
        """TBW.

        :param ds9_exe:
        """
        self._ds9_exe = os.path.abspath(ds9_exe)
        self._ds9_dir = os.path.dirname(self._ds9_exe)

        # TODO: this assumes xpa tools are in the ds9 directory (for *unix this is not the case)
        self._xpaget_exe = os.path.join(self._ds9_dir, 'xpaget')
        self._xpaset_exe = os.path.join(self._ds9_dir, 'xpaset')

    def is_ready(self):
        """Check if the ds9 application is listening."""
        try:
            self.xpaget()
            return True
        except DS9Exception as _:
            return False

    def start(self):
        """Check if the ds9 application is listening, if not, then start it up."""
        if not self.is_ready():
            # os.system('start %s %s %s' % (self._ds9_exe, '-xpa', 'localhost'))
            detached_process = 0x00000008
            subprocess.Popen([self._ds9_exe, '-xpa', 'localhost'],
                             cwd=self._ds9_dir,
                             shell=False,
                             close_fds=True,
                             creationflags=detached_process)

            for _ in range(10):
                time.sleep(0.5)
                if self.is_ready():
                    break

        if not self.is_ready():
            raise DS9Exception('Failed to start DS9 in XPA communication mode')

    def xpaset(self, cmd, arg, stdin_input=None):
        """Execute a XPA set command."""
        if stdin_input is None:
            args = [self._xpaset_exe, '-p', 'ds9']
        else:
            args = [self._xpaset_exe, 'ds9']

        if cmd:
            args.append(cmd)

        if arg:
            args.append(arg)

        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=stdin_input,
            universal_newlines=True  # this converts line termination to \n
        )
        stdout_stderr = process.communicate()
        if len(stdout_stderr[0]):
            raise DS9Exception(stdout_stderr[0])

    def xpaget(self, cmd=None, arg=None):
        """Execute a XPA get command."""
        args = [self._xpaget_exe, 'ds9']

        if cmd:
            args.append(cmd)

        if arg:
            args.append(arg)

        process = subprocess.Popen(
            args,  # this will simply list the available commands
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True  # this converts line termination to \n
        )
        stdout, stderr = process.communicate()

        if len(stderr):
            raise DS9Exception(stderr)

        return stdout

    def view_fits(self, file_path, new_frame=False):
        """View a fits file in the running ds9 application."""
        if new_frame:
            self.xpaset('frame', 'new')

        with open(file_path, 'rb') as file_obj:
            self.xpaset('fits', os.path.basename(file_path), stdin_input=file_obj)
