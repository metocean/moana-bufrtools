#!/usr/bin/env python
import os
import glob


class MOANA_public_data():
    """
    Data available to share by serial number from the Moana project in Aoteaora New Zealand
    """

    def __init__(self, serial_number, input_directory):
        self.serial_number = serial_number
        self.input_directory = input_directory

    def find_files(self, serial_number):
        number_string = "%04d" % serial_number
        self.public_files = sorted(
            glob.glob(
                os.path.join(self.input_directory, "MOANA_{}*.nc".format(number_string))
            )
        )
        return self.public_files

    def run(self):
        self.find_files(self.serial_number)


if __name__ == "__main__":
    pass
