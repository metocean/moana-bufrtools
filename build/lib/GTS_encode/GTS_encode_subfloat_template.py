#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Encoding support for mangopare sensors.
This encoding uses the toolbox developed by eccodes and it is adapted to encode mangopare sensors using the template for Temperature and salinity profile observed by profile floats

The code of this template is (315003)  
Category 15 – Oceanographic report sequence 
003 – Temperature and salinity profile observed by profile floats

        # 
        301011 Time
        005001 Latitude
        006001 Longitude
        008080 Qualifier for GTSPP Quality Flag
        033050 Global GTSPP Quality Flag
        007065 Water Pressure (Pa)
        008080 Qualifier for GTSPP Quality Flag
        033050 Global GTSPP Quality Flag
        022045 Oceanographic Water Temperature (K)

Mangopare sensor has the depth in meters - this is converted to dbars then to Pa
Mangopare provides the temperature in Celsius - this is converted to Kelvin 

There are two classes included here

"""

import numpy as np
import xarray as xr
from eccodes import (
    codes_set,
    codes_set_array,
    codes_write,
    codes_release,
    codes_bufr_new_from_samples,
)
from eccodes import *
from utils import pres


class GTS_encode_subfloat:
    def __init__(self, filename, centre_code):
        self.filename = filename
        self.centre_code = centre_code

    def create_variables_from_netcdf(self):
        self.ds = xr.open_dataset(self.filename)
        self.df = self.ds.to_dataframe()
        QC = np.where(self.df["QC_FLAG"] == 1)[0]
        self.df = self.df.iloc[QC]
        self.df["PRESSURE"] = pres(self.df["DEPTH"], self.df["LATITUDE"])
        self.years = self.df.index.year.values
        self.months = self.df.index.month.values
        self.days = self.df.index.day.values
        self.hours = self.df.index.hour.values
        self.minutes = self.df.index.minute.values
        self.seconds = self.df.index.second.values
        self.latitudes = self.df["LATITUDE"].values
        self.longitudes = self.df["LONGITUDE"].values
        self.pressures = np.round(self.df["PRESSURE"].values, 2)
        self.temperatures = self.df["TEMPERATURE"].values + 273.15
        self.output_filename = self.filename[0:-3] + ".bufr"

    def create_bufr_file(self):
        VERBOSE = 1  # verbose error reporting
        ibufr = codes_bufr_new_from_samples("BUFR3_local")
        #######################################
        #########Section 1, Header ############
        #######################################
        codes_set(ibufr, "edition", 3)
        codes_set(ibufr, "masterTableNumber", 0)
        codes_set(ibufr, "bufrHeaderSubCentre", 0)
        codes_set(ibufr, "bufrHeaderCentre", self.centre_code)
        codes_set(ibufr, "updateSequenceNumber", 0)
        codes_set(ibufr, "dataCategory", 31)  # CREX Table A 31 -> Oceanographic Data
        # codes_set(ibufr, "dataSubCategory", 182) #International data-subcategory
        codes_set(
            ibufr, "masterTablesVersionNumber", 28
        )  # Latest version 28 -> 15 November 2021
        codes_set(ibufr, "localTablesVersionNumber", 0)
        codes_set(ibufr, "typicalYearOfCentury", int(str(self.years[0])[2::]))
        codes_set(ibufr, "typicalMonth", int(self.months[0]))
        codes_set(ibufr, "typicalDay", int(self.days[0]))
        codes_set(ibufr, "typicalHour", int(self.hours[0]))
        codes_set(ibufr, "typicalMinute", int(self.minutes[0]))
        codes_set(ibufr, "numberOfSubsets", 1)
        codes_set(ibufr, "observedData", 1)
        codes_set(ibufr, "compressedData", 0)

        ################################################
        #########Section 3, DataDescription ############
        ################################################
        codes_set(
            ibufr, "inputExtendedDelayedDescriptorReplicationFactor", len(self.df)
        )
        codes_set(ibufr, "unexpandedDescriptors", (315003))

        # Create the structure of the data section
        codes_set(
            ibufr, "marineObservingPlatformIdentifier", int(self.ds.moana_serial_number)
        )
        codes_set(ibufr, "observingPlatformManufacturerModel", "Mangopare")
        codes_set(
            ibufr,
            "observingPlatformManufacturerSerialNumber",
            self.ds.deck_unit_serial_number,
        )
        codes_set(ibufr, "buoyType", 2)  # CODE-Table 2 -> subsurface float, moving
        codes_set(ibufr, "dataCollectionLocationSystem", 2)  # CODE_Table 2 -> GPS
        codes_set(
            ibufr, "dataBuoyType", 8
        )  # CODE-Table  8 -> Unspecified subsurface float
        codes_set(ibufr, "directionOfProfile", 3)  # CODE-Table 3-> Missing value
        codes_set(
            ibufr, "instrumentTypeForWaterTemperatureOrSalinityProfileMeasurement", 995
        )  # CODE-Table 995 -> Marine mammal

        #####################################
        #########Section 4, Data ############
        #####################################
        codes_set_array(ibufr, "waterPressure", self.pressures)
        codes_set_array(ibufr, "#1#year", self.years)
        codes_set_array(ibufr, "#1#month", self.months)
        codes_set_array(ibufr, "#1#day", self.days)
        codes_set_array(ibufr, "#1#hour", self.hours)
        codes_set_array(ibufr, "#1#minute", self.minutes)
        codes_set_array(ibufr, "#1#latitude", self.latitudes)
        codes_set_array(ibufr, "#1#longitude", self.longitudes)
        codes_set_array(ibufr, "oceanographicWaterTemperature", self.temperatures)
        codes_set(ibufr, "salinity", CODES_MISSING_DOUBLE)  # NO Salinity Data
        ### This bit includes the quality flags for each measurement
        ## There's three because there is a quality flag for depth, for temperature and for salinity
        for i in range(0, len(self.df) * 3, 3):
            key1 = "#" + str(i + 1) + "#QualifierForGTSPPQualityFlag"
            key2 = "#" + str(i + 2) + "#QualifierForGTSPPQualityFlag"
            key3 = "#" + str(i + 3) + "#QualifierForGTSPPQualityFlag"
            key1G = "#" + str(i + 1) + "#GlobalGTSPPQualityFlag"
            key2G = "#" + str(i + 2) + "#GlobalGTSPPQualityFlag"
            key3G = "#" + str(i + 3) + "#GlobalGTSPPQualityFlag"
            codes_set(
                ibufr, key1, 10
            )  # CODE-Table 0 08 080 -> 10 Water pressure at a level
            codes_set(
                ibufr, key2, 11
            )  # CODE-Table 0 08 080 -> 11 Water temperature at a level
            codes_set(ibufr, key3, 63)  # CODE-Table 0 08 080 -> 63 Missing value
            codes_set(
                ibufr, key1G, 9
            )  # CODE-Table 0 33 050 -> 9 Good for operational use Missing value
            codes_set(
                ibufr, key2G, 9
            )  # CODE-Table 0 33 050 -> 9 Good for operational use Missing value
            codes_set(ibufr, key3G, 15)  # CODE-Table 0 33 050 -> 15 Missing value
        # Encode the keys back in the data section
        codes_set(ibufr, "pack", 1)
        # Create output file
        output_filename = open(self.output_filename, "wb")
        # Write encoded data into a file and close
        codes_write(ibufr, output_filename)
        print("Created output BUFR file ", output_filename)
        codes_release(ibufr)

    def run(self):
        self.create_variables_from_netcdf()
        self.create_bufr_file()


class GTS_encode_subset_subfloat:
    def __init__(self, filename, centre_code):
        self.filename = filename
        self.centre_code = centre_code

    def create_variables_from_netcdf(self):
        self.ds = xr.open_dataset(self.filename)
        self.df = self.ds.to_dataframe()
        QC = np.where(self.df["QC_FLAG"] == 1)[0]
        self.df = self.df.iloc[QC]
        self.df["PRESSURE"] = (
            pres(self.df["DEPTH"], self.df["LATITUDE"]) * 10000
        )  # Conversion meters to Pa
        self.years = self.df.index.year.values
        self.months = self.df.index.month.values
        self.days = self.df.index.day.values
        self.hours = self.df.index.hour.values
        self.minutes = self.df.index.minute.values
        self.seconds = self.df.index.second.values
        self.latitudes = self.df["LATITUDE"].values
        self.longitudes = self.df["LONGITUDE"].values
        self.pressures = np.round(self.df["PRESSURE"].values, 2)
        self.temperatures = (
            self.df["TEMPERATURE"].values + 273.15
        )  # Conversion Celsius to Kelvin
        self.output_filename = self.filename[0:-3] + ".bufr"

    def create_bufr_file(self):
        VERBOSE = 1  # verbose error reporting
        ibufr = codes_bufr_new_from_samples("BUFR3_local")
        #######################################
        #########Section 1, Header ############
        #######################################
        codes_set(ibufr, "edition", 3)
        codes_set(ibufr, "masterTableNumber", 0)
        codes_set(ibufr, "bufrHeaderSubCentre", 0)
        codes_set(ibufr, "bufrHeaderCentre", self.centre_code)
        codes_set(ibufr, "updateSequenceNumber", 0)
        codes_set(ibufr, "dataCategory", 31)  # CREX Table A 31 -> Oceanographic Data
        # codes_set(ibufr, "dataSubCategory", 182) #International data-subcategory
        codes_set(
            ibufr, "masterTablesVersionNumber", 28
        )  # Latest version 28 -> 15 November 2021
        codes_set(ibufr, "localTablesVersionNumber", 0)
        codes_set(ibufr, "typicalYearOfCentury", int(str(self.years[0])[2::]))
        codes_set(ibufr, "typicalMonth", int(self.months[0]))
        codes_set(ibufr, "typicalDay", int(self.days[0]))
        codes_set(ibufr, "typicalHour", int(self.hours[0]))
        codes_set(ibufr, "typicalMinute", int(self.minutes[0]))
        codes_set(ibufr, "numberOfSubsets", 1)
        codes_set(ibufr, "observedData", 1)
        codes_set(ibufr, "compressedData", 0)

        ################################################
        #########Section 3, DataDescription ############
        ################################################
        codes_set(
            ibufr, "inputExtendedDelayedDescriptorReplicationFactor", 9 * len(self.df)
        )  ##Each observation in each file is a subset, each subset contains 9 variables
        codes_set(ibufr, "unexpandedDescriptors", (315003))

        # Create the structure of the data section
        codes_set(
            ibufr, "marineObservingPlatformIdentifier", int(self.ds.moana_serial_number)
        )
        codes_set(ibufr, "observingPlatformManufacturerModel", "Mangopare")
        codes_set(
            ibufr,
            "observingPlatformManufacturerSerialNumber",
            self.ds.deck_unit_serial_number,
        )
        codes_set(ibufr, "buoyType", 2)  # CODE-Table 2 -> subsurface float, moving
        codes_set(ibufr, "dataCollectionLocationSystem", 2)  # CODE_Table 2 -> GPS
        codes_set(
            ibufr, "dataBuoyType", 8
        )  # Code-Table  8 -> Unspecified subsurface float
        codes_set(ibufr, "directionOfProfile", 3)  # Code-Table 3-> Missing value
        codes_set(
            ibufr, "instrumentTypeForWaterTemperatureOrSalinityProfileMeasurement", 995
        )

        #####################################
        #########Section 4, Data ############
        #####################################
        codes_set_array(ibufr, "#1#waterPressure", self.pressures)
        codes_set(ibufr, "#1#QualifierForGTSPPQualityFlag", 10)
        codes_set(ibufr, "#1#GlobalGTSPPQualityFlag", 9)
        codes_set_array(ibufr, "#1#year", self.years)
        codes_set_array(ibufr, "#1#month", self.months)
        codes_set_array(ibufr, "#1#day", self.days)
        codes_set_array(ibufr, "#1#hour", self.hours)
        codes_set_array(ibufr, "#1#minute", self.minutes)
        codes_set_array(ibufr, "#1#latitude", self.latitudes)
        codes_set_array(ibufr, "#1#longitude", self.longitudes)
        codes_set_array(ibufr, "#1#oceanographicWaterTemperature", self.temperatures)
        codes_set(ibufr, "#2#QualifierForGTSPPQualityFlag", 11)
        codes_set(ibufr, "#2#GlobalGTSPPQualityFlag", 9)
        codes_set(ibufr, "#1#salinity", CODES_MISSING_DOUBLE)  # NO Salinity Data

        # Encode the keys back in the data section
        codes_set(ibufr, "pack", 1)
        # Create output file
        output_filename = open(self.output_filename, "wb")
        # Write encoded data into a file and close
        codes_write(ibufr, output_filename)
        print("Created output BUFR file ", output_filename)
        codes_close(output_filename)
        codes_release(ibufr)

    def run(self):
        self.find_files(self.serial_number)
        public_files = self.public_files
        for files in public_files:
            self.create_variables_from_netcdf(self.output_filename)
            self.create_bufr_file(files)
