
import logging
import subprocess
import time
import glob
import shutil

class GTS(object):
    """
    A class that wraps the functionality of transferring files using curl.

    Args:
        filelist (list): A list of files to transfer.
        logger (logging.Logger): An instance of the logger class for logging messages.
    """

    def __init__(
        self,
        path='/data/obs/GTS/',
        transfer_path='/data/obs/GTS/transfer/',
        logger=logging,
        **kwargs,
    ):
        self.path = path
        self.transfer_path = transfer_path
        self.logger = logger

    def run(self):
        """
        Transfers the files in the filelist using curl.

        Raises:
            Exception: If no files are found in the filelist.
        """
        filelist = sorted(glob.glob(f"{self.path}*.bufr"))
        try:
            for file in filelist:
                jobstr = f"curl -X PUT --data-binary @{file} http://kt-mhs01.met.co.nz:11120/mhs/queue"
                proc = subprocess.run(
                    jobstr, shell=True, check=True, capture_output=True
                )
                # time.sleep(5)
                shutil.move(file, f"{self.transfer_path}{file.split('/')[-1]}")
        except Exception as exc:
            self.logger.error("No files to publish")
            raise type(exc)(f"No file list found due to: {exc}")

class dataserv(object):
    """
    A class that wraps the functionality of transferring files using curl.

    Args:
        filelist (list): A list of files to transfer.
        logger (logging.Logger): An instance of the logger class for logging messages.
    """

    def __init__(
        self,
        filelist=None,
        destination='metocean@dataserv2.hm:/hub/data/obs/GTS/',
        logger=logging,
        **kwargs,
    ):
        self.filelist = filelist
        self.destination = destination
        self.logger = logger

    def run(self):
        """
        Transfers the files in the filelist using rsync

        Raises:
            Exception: If no files are found in the filelist.
        """
        filelist = self.filelist
        try:
            for files in filelist:
                jobstr = f"rsync -av {files}  {self.destination}"
                proc = subprocess.run(
                    jobstr, shell=True, check=True, capture_output=True
                )
                # time.sleep(5)
        except Exception as exc:
            self.logger.error("No files to send")
            raise type(exc)(f"No file list found due to: {exc}")
