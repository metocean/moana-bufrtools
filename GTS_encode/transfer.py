
import logging
import subprocess
import time


class Wrapper(object):
    """
    A class that wraps the functionality of transferring files using curl.

    Args:
        filelist (list): A list of files to transfer.
        logger (logging.Logger): An instance of the logger class for logging messages.
    """

    def __init__(
        self,
        filelist=None,
        logger=logging,
        **kwargs,
    ):
        self.filelist = filelist
        self.logger = logger

    def run(self):
        """
        Transfers the files in the filelist using curl.

        Raises:
            Exception: If no files are found in the filelist.
        """
        filelist = self.filelist
        try:
            for file in filelist:
                jobstr = f"curl -X PUT --data-binary {file} http://kt-mhs01.met.co.nz:11120/mhs/queue"
                proc = subprocess.run(
                    jobstr, shell=True, check=True, capture_output=True
                )
                # time.sleep(5)
        except Exception as exc:
            self.logger.error("No files to publish")
            raise type(exc)(f"No file list found due to: {exc}")