import os
import logging
import numpy as np
import pandas as pd
import xarray as xr
import seawater as sw
import datetime as dt
from glob import glob
xr.set_options(keep_attrs=True)

# cycle_dt = dt.datetime.utcnow()

def keep_numbers_only(s):
    return ''.join(c for c in s if c.isdigit())


class Wrapper(object):
    """
    Wrapper class for publication of observational data onto THREDDS servers.
    Takes a list of quality-controlled netcdf files and reformats the ones available
    for public access using CF-1.6 conventions and following IMOS and ARGOS conventions
    IMOS: https://s3-ap-southeast-2.amazonaws.com/content.aodn.org.au/Documents/IMOS/Conventions/IMOS_NetCDF_Conventions.pdf
    ARGOS: https://archimer.ifremer.fr/doc/00187/29825/94819.pdf

    Arguments:
        filelist -- list of files to apply transformation to
        outfile_ext -- extension to add to filenames when saving as netcdf files
        out_dir - directory to save public netcdf files (to send to THREDDS server)
        qc_class -- python class wrapper for running qc tests, returns updated xarray dataset
            that includes qc flags and updated status_file
        attr_file -- location of attribute_list.yml, default uses the one in the python
            package, should be a yaml file (see sample one in ops_qc directory)

    Returns:
        self._success_files -- list of files successfully reformatted and saved as new netcdf files

    Outputs:
        Saves public files as netcdf in out_dir
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
        try:
            # Check if data is public
            public = xr.open_dataset(filename, cache=False, engine="netcdf4").attrs[
                "public"
            ]
            self.wigos_id = xr.open_dataset(filename, cache=False, engine="netcdf4").attrs[
                "wigos_id"
            ]
            
            # Check if the current data is after the agreement signature date
            self.first_measurement = xr.open_dataset(
                filename, cache=False, engine="netcdf4"
            )[self.time_varname_source][0].values
            self.last_measurement = xr.open_dataset(
                filename, cache=False, engine="netcdf4"
            )[self.time_varname_source][-1].values
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
        if hasattr(self, "_success_files") and not self.filelist:
            self.filelist = self._success_files
        if not self.filelist:
            self.logger.error(
                "No file list found, please specify.  No transformation for publication performed."
            )

    def run(self):
        self._set_filelist()
        exec(
            f"from GTS_encode.GTS_encode import {self.GTS_template} as GTS_encode"
        )
        for file in self.filelist:
            if self._available_for_GTS_publication(file):
                self.filename = file
                # create (mkdir) out_dir if it doesn't exist
                self._initialize_outdir(self.out_dir)
                GTS=GTS_encode(self.filename, self.centre_code, out_dir=self.out_dir)
                GTS_filename=GTS.run()
                self._saved_files["filelist"].append(GTS_filename)
        return self._saved_files
