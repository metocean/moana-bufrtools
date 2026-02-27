import unittest
from unittest.mock import patch
from GTS_encode import GTS_encode_subfloat, GTS_encode_ship

class TestGTS_encode(unittest.TestCase):

    def test_GTS_encode_subfloat_create_variables_from_netcdf(self):
        filename = "/path/to/file.nc"
        database_dict = {
            "centre code": 69,
            "internal ship id": "SHIP123",
            "sensor model": "Sensor Model",
            "sensor serial": "Sensor Serial"
        }
        upcast = True
        QC_flag = 1
        gts_encode = GTS_encode_subfloat(filename, database_dict, upcast, QC_flag)
        gts_encode.create_variables_from_netcdf()
        # Add assertions here to validate the variables extracted from the NetCDF file

    def test_GTS_encode_subfloat_create_bufr_file(self):
        filename = "/path/to/file.nc"
        database_dict = {
            "centre code": 69,
            "internal ship id": "SHIP123",
            "sensor model": "Sensor Model",
            "sensor serial": "Sensor Serial"
        }
        upcast = True
        QC_flag = 1
        gts_encode = GTS_encode_subfloat(filename, database_dict, upcast, QC_flag)
        gts_encode.create_variables_from_netcdf()
        gts_encode.create_bufr_file()
        # Add assertions here to validate the creation of the BUFR file

    def test_GTS_encode_ship_create_variables_from_netcdf(self):
        filename = "/path/to/file.nc"
        centre_code = 69
        outdir = "/path/to/output"
        upcast = True
        QC_flag = 1
        gts_encode = GTS_encode_ship(filename, centre_code, outdir, upcast, QC_flag)
        gts_encode.create_variables_from_netcdf()
        # Add assertions here to validate the variables extracted from the NetCDF file

    def test_GTS_encode_ship_create_bufr_file(self):
        filename = "/path/to/file.nc"
        centre_code = 69
        outdir = "/path/to/output"
        upcast = True
        QC_flag = 1
        gts_encode = GTS_encode_ship(filename, centre_code, outdir, upcast, QC_flag)
        gts_encode.create_variables_from_netcdf()
        gts_encode.create_bufr_file()
        # Add assertions here to validate the creation of the BUFR file

if __name__ == "__main__":
    unittest.main()