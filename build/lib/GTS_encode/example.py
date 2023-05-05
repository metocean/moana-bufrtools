from MOANA_public_data import MOANA_public_data
from GTS_encode import GTS_encode

input_directory = "/data/obs/mangopare/GTS"
serial_number = 58
mpd = MOANA_public_data(serial_number, input_directory)
files = mpd.find_files(serial_number)
centre_code = (
    69  # MetService Centre code from table Code Table C-11 69 -> Wellington (RSMC)
)
for file in files:
    #    GTS = GTS_encode_subfloat(file, centre_code)
    GTS = GTS_encode_ship(file, centre_code)
    GTS.create_variables_from_netcdf()
    GTS.create_bufr_file()
