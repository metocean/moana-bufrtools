import os
import logging
import numpy as np
import pandas as pd
import xarray as xr
import seawater as sw
import datetime as dt
from glob import glob
import importlib
xr.set_options(keep_attrs=True)

# cycle_dt = dt.datetime.utcnow()

def keep_numbers_only(s):
    return ''.join(c for c in s if c.isdigit())


class Wrapper(object):
    """
    A class that wraps the GTS encoding functionality.

    Args:
        filelist (list): A list of file paths to be processed.
        out_dir (str): The output directory where the encoded files will be saved.
        GTS_template (str): The GTS template to be used for encoding.
        centre_code (int): The center code for the GTS encoding.
        logger (logging.Logger): The logger object for logging messages.
        **kwargs: Additional keyword arguments.

    Methods:
        _available_for_GTS_publication: Checks if the data is available for GTS publication.
        _initialize_outdir: Initializes the output directory.
        _set_filelist: Sets the filelist attribute.
        run: Runs the GTS encoding process.

    Returns:
        dict: A dictionary containing the saved files.
    """
    def __init__(
        self,
        filelist=None,
        out_dir=None,
        GTS_template="GTS_encode_ship",
        centre_code=69,
        logger=logging,
        **kwargs,
    ):
        self.filelist = filelist
        self.out_dir = out_dir
        self.logger = logging
        self.GTS_template=GTS_template
        self.centre_code = centre_code
        self._saved_files = {"filelist": []}

    def _available_for_GTS_publication(self, filename):
        """
        Checks if the data in the given file is available for GTS (Global Telecommunication System) publication.

        Args:
            filename (str): The path to the file containing the data.

        Returns:
            bool: True if the data is available for GTS publication, False otherwise.
        """
        try:
            public = xr.open_dataset(filename, cache=False, engine="netcdf4").attrs[
                "public"
            ]
            self.wigos_id = xr.open_dataset(filename, cache=False, engine="netcdf4").attrs[
                "wigos_id"
            ]
            
            # Check if the current data is after the agreement signature date
            self.first_measurement = xr.open_dataset(
                filename, cache=False, engine="netcdf4"
            )['DATETIME'][0].values
            self.last_measurement = xr.open_dataset(
                filename, cache=False, engine="netcdf4"
            )['DATETIME'][-1].values
            publication_date = dt.datetime.strptime(
                xr.open_dataset(filename, cache=False, engine="netcdf4").attrs[
                    "publication_date"
                ],
                "%d/%m/%Y",
            )
            publication_date = np.datetime64(publication_date)
            if (self.first_measurement - publication_date > 0) & (self.wigos_id != "nan"):
                return eval(public)
            else:
                return False
        except:
            return False

    def _initialize_outdir(self, dir_path):
        """
        Check if outdir exists, create if not
        """
        try:
            if not os.path.isdir(dir_path):
                os.mkdir(dir_path)
        except Exception as exc:
            self.logger.error(
                "Could not create specified directory to save publishable files in: {}".format(
                    exc
                )
            )
        
    def _set_filelist(self):
            """
            Sets the file list for transformation.

            If the `_success_files` attribute is present and the `filelist` attribute is empty,
            the `_success_files` attribute is assigned to the `filelist` attribute.

            If the `filelist` attribute is still empty after the above check,
            an error message is logged indicating that no file list was found.

            This method is responsible for setting the file list that will be used for transformation
            before publication.

            Returns:
                None
            """
            if hasattr(self, "_success_files") and not self.filelist:
                self.filelist = self._success_files
            if not self.filelist:
                self.logger.error(
                    "No file list found, please specify.  No transformation for publication performed."
                )

    def run(self):
        """
        Runs the GTS encoding process for each file in the filelist.

        Returns:
            dict: A dictionary containing the saved files.
        """
        self._set_filelist()
        GTS_encode_module = importlib.import_module('GTS_encode.GTS_encode')
        GTS_encoding = getattr(GTS_encode_module, self.GTS_template)
        for file in self.filelist:
            if self._available_for_GTS_publication(file):
                self.filename = file
                # create (mkdir) out_dir if it doesn't exist
                self._initialize_outdir(self.out_dir)
                GTS = GTS_encoding(self.filename, self.centre_code, outdir=self.out_dir)
                GTS_filename = GTS.run()
                self._saved_files["filelist"].append(GTS_filename)
        return self._saved_files
