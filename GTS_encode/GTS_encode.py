#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Encoding support for mangopare sensors.
"""

import numpy as np
import xarray as xr
from eccodes import (
    codes_set,
    codes_set_array,
    codes_write,
    codes_release,
    codes_bufr_new_from_samples,
    codes_set_missing,
)
from eccodes import *
from utils import pres, extract_upcast
import pdb


class GTS_encode_subfloat:
    def __init__(self, filename, centre_code, upcast=True, QC_flag=1):
        self.filename = filename
        self.centre_code = centre_code
        self.upcast = upcast
        self.qcflag = QC_flag

    def create_variables_from_netcdf(self):
        self.ds = xr.open_dataset(self.filename)
        self.df = self.ds.to_dataframe()
        if self.qcflag == 1:
            QC = np.where(self.df["QC_FLAG"] == self.qcflag)[0]
        elif len(self.qcflag) == 2:
            QC = np.where(
                (self.df["QC_FLAG"] == self.qcflag[0])
                | (self.df["QC_FLAG"] == self.qcflag[1])
            )[0]
        self.df = self.df.iloc[QC]
        if self.upcast:
            self.df = extract_upcast(self.df)
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
        if self.upcast:
            codes_set(ibufr, "directionOfProfile", 0)
        else:
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
        codes_set_missing(ibufr, "salinity")  # NO Salinity Data
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


class GTS_encode_ship:
    def __init__(self, filename, centre_code, upcast=True, QC_flag=1):
        self.filename = filename
        self.centre_code = centre_code
        self.upcast = upcast
        self.qcflag = QC_flag

    def create_variables_from_netcdf(self):
        self.ds = xr.open_dataset(self.filename)
        self.df = self.ds.to_dataframe()
        if self.qcflag == 1:
            QC = np.where(self.df["QC_FLAG"] == self.qcflag)[0]
        elif len(self.qcflag) == 2:
            QC = np.where(
                (self.df["QC_FLAG"] == self.qcflag[0])
                | (self.df["QC_FLAG"] == self.qcflag[1])
            )[0]
        self.df = self.df.iloc[QC]
        if self.upcast:
            self.df = extract_upcast(self.df)
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
        self.depths = self.df["DEPTH"].values
        self.temperatures = self.df["TEMPERATURE"].values + 273.15
        self.output_filename = self.filename[0:-3] + ".bufr"
        self.profile_name = self.filename.split("_")[-2]

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
        # Each value of replication factor relates to the observations of the profiles,
        # as we don't have values for the current and dissolved oxygen profile the replication factor is set to 1.
        # In case this data was to be added the number of replications should be updated
        # according to the number of measurements for these profles.
        codes_set_array(
            ibufr,
            "inputExtendedDelayedDescriptorReplicationFactor",
            [len(self.df), 1, 1],
        )
        codes_set(ibufr, "unexpandedDescriptors", 315007)
        ############################################
        # Create the structure of the data section #
        ############################################
        codes_set(ibufr, "shipOrMobileLandStationIdentifier", self.ds.vessel_id)
        codes_set(
            ibufr, "marineObservingPlatformIdentifier", int(self.ds.moana_serial_number)
        )
        #        codes_set(
        #            ibufr, "agencyInChargeOfOperatingObservingPlatform", self.ds.platform_code
        #        )
        codes_set(ibufr, "identifierOfTheCruiseOrMission", self.ds.platform_code)
        codes_set(ibufr, "uniqueIdentifierForProfile", self.profile_name)
        codes_set(ibufr, "year", int(self.years[-1]))
        codes_set(ibufr, "month", int(self.months[-1]))
        codes_set(ibufr, "day", int(self.days[-1]))
        codes_set(ibufr, "hour", int(self.hours[-1]))
        codes_set(ibufr, "minute", int(self.minutes[-1]))
        codes_set(ibufr, "latitude", self.latitudes[-1])
        codes_set(ibufr, "longitude", self.longitudes[-1])
        codes_set(ibufr, "totalWaterDepth", self.depths.max())
        codes_set(
            ibufr,
            "#1#instrumentTypeForWaterTemperatureOrSalinityProfileMeasurement",
            902,
        )
        codes_set(
            ibufr,
            "#1#instrumentSerialNumberForWaterTemperatureProfile",
            self.ds.moana_serial_number,
        )
        #####################################
        #########Section 4, Data ############
        #####################################
        ## Surface Measurements ##
        ##########################
        # At the moment we are extracting the first value of the profile
        ## Surface Temperature
        codes_set(ibufr, "#1#methodOfWaterTemperatureAndOrOrSalinityMeasurement", 15)
        codes_set(ibufr, "#1#oceanographicWaterTemperature", self.temperatures[0])
        codes_set(
            ibufr, "#1#depthBelowWaterSurface", self.depths[0] * 100
        )  # data must be provided in cm
        ##Surface Salinity
        codes_set_missing(ibufr, "#1#methodOfSalinityOrDepthMeasurement")
        codes_set_missing(ibufr, "#2#depthBelowWaterSurface")
        codes_set_missing(ibufr, "#1#salinity")
        ##Surface Current
        codes_set_missing(ibufr, "#1#methodOfSeaOrWaterCurrentMeasurement")
        codes_set_missing(
            ibufr, "#1#methodOfRemovingVelocityAndMotionOfPlatformFromCurrent"
        )
        codes_set_missing(ibufr, "#1#durationAndTimeOfCurrentMeasurement")
        codes_set_missing(ibufr, "#1#seaSurfaceCurrentDirection")
        codes_set_missing(ibufr, "#1#speedOfSeaSurfaceCurrent")
        ## Profile Measurements ##
        ##########################
        ##Temperature and salinity profile
        codes_set_missing(
            ibufr, "#2#instrumentTypeForWaterTemperatureOrSalinityProfileMeasurement"
        )
        codes_set_missing(
            ibufr,
            "#2#instrumentSerialNumberForWaterTemperatureProfile",
        )
        codes_set(ibufr, "#2#methodOfWaterTemperatureAndOrOrSalinityMeasurement", 14)
        codes_set(
            ibufr,
            "#3#instrumentTypeForWaterTemperatureOrSalinityProfileMeasurement",
            902,
        )
        codes_set(ibufr, "#1#waterTemperatureProfileRecorderTypes", 99)
        codes_set(
            ibufr,
            "#3#instrumentSerialNumberForWaterTemperatureProfile",
            self.ds.moana_serial_number,
        )
        codes_set(ibufr, "#2#methodOfSalinityOrDepthMeasurement", 1)
        codes_set(ibufr, "#1#indicatorForDigitization", 0)
        if self.upcast:
            codes_set(ibufr, "#1#directionOfProfile", 0)  # Code-Table 0-> upward
        else:
            codes_set(
                ibufr, "#1#directionOfProfile", 3
            )  # Code-Table 3 -> missing value
        codes_set(ibufr, "#1#methodOfDepthCalculation", 1)
        ### This bit includes the quality flags and data for each measurement
        ## Quality flags must be cycled every four, as the four variables need an associated QF
        for count, i in enumerate(range(0, len(self.df) * 4, 4)):
            key1 = "#" + str(i + 1) + "#QualifierForGTSPPQualityFlag"
            key2 = "#" + str(i + 2) + "#QualifierForGTSPPQualityFlag"
            key3 = "#" + str(i + 3) + "#QualifierForGTSPPQualityFlag"
            key4 = "#" + str(i + 4) + "#QualifierForGTSPPQualityFlag"
            key1G = "#" + str(i + 1) + "#GlobalGTSPPQualityFlag"
            key2G = "#" + str(i + 2) + "#GlobalGTSPPQualityFlag"
            key3G = "#" + str(i + 3) + "#GlobalGTSPPQualityFlag"
            key4G = "#" + str(i + 4) + "#GlobalGTSPPQualityFlag"
            depth_key = "#" + str(count + 3) + "#depthBelowWaterSurface"
            pressure_key = "#" + str(count + 1) + "#waterPressure"
            temp_key = "#" + str(count + 2) + "#oceanographicWaterTemperature"
            salt_key = "#" + str(count + 2) + "#salinity"
            codes_set(ibufr, depth_key, self.depths[count])
            codes_set(ibufr, key1, 13)  # Depth Quality Flags
            codes_set(ibufr, key1G, 9)  # Depth Quality Flags
            codes_set(ibufr, pressure_key, self.pressures[count])
            codes_set(ibufr, key2, 10)  # Pressure Quality Flags
            codes_set(ibufr, key2G, 9)  # Pressure Quality Flags
            codes_set(ibufr, temp_key, self.temperatures[count])
            codes_set(ibufr, key3, 11)  # Temperature Quality Flags
            codes_set(ibufr, key3G, 9)  # Temperature Quality Flags
            codes_set_missing(ibufr, salt_key)
            codes_set(ibufr, key4, 63)  # Salinity Quality Flags/Missing data
            codes_set(ibufr, key4G, 15)  # Salinity Quality Flags/Missing data
        ### This bit includes the quality flags for each measurement
        ## There's three because there is a quality flag for depth, for temperature and for salinity
        ##Current profile
        # As no data is provided everything is set to missing
        codes_set_missing(ibufr, "#2#indicatorForDigitization")
        codes_set_missing(ibufr, "#2#methodOfSeaOrWaterCurrentMeasurement")
        codes_set_missing(
            ibufr, "#2#methodOfRemovingVelocityAndMotionOfPlatformFromCurrent"
        )
        codes_set_missing(ibufr, "#2#durationAndTimeOfCurrentMeasurement")
        codes_set_missing(ibufr, "#2#directionOfProfile")  # Code-Table 0-> upward
        codes_set_missing(ibufr, "#2#methodOfDepthCalculation")
        codes_set_missing(ibufr, "#" + str(count + 4) + "#depthBelowWaterSurface")
        codes_set_missing(ibufr, "#" + str(count + 2) + "#waterPressure")
        codes_set_missing(ibufr, "#2#waterPressure")
        codes_set_missing(ibufr, "#1#speedOfCurrent")
        codes_set_missing(ibufr, "#1#CurrentDirection")
        ##Dissolved oxygen data
        # As no data is provided everything is set to missing
        codes_set_missing(ibufr, "#3#indicatorForDigitization")
        codes_set_missing(ibufr, "#3#methodOfDepthCalculation")
        codes_set_missing(ibufr, "#" + str(count + 5) + "#depthBelowWaterSurface")
        codes_set_missing(ibufr, "#" + str(count + 3) + "#waterPressure")
        codes_set_missing(
            ibufr, "#1#instrumentTypeOrSensorForDissolvedOxygenMeasurement"
        )
        codes_set_missing(ibufr, "#1#oceanographicDissolvedOxygen")
        # Encode the keys back in the data section #
        ############################################
        codes_set(ibufr, "pack", 1)
        # Create output file #
        ######################
        output_filename = open(self.output_filename, "wb")
        # Write encoded data into a file and close
        codes_write(ibufr, output_filename)
        print("Created output BUFR file ", output_filename)
        codes_release(ibufr)

    def run(self):
        self.create_variables_from_netcdf()
        self.create_bufr_file()


class GTS_encode_glider:
    def __init__(self, filename, centre_code, upcast=True, QC_flag=1):
        self.filename = filename
        self.centre_code = centre_code
        self.upcast = upcast
        self.qcflag = QC_flag

    def create_variables_from_netcdf(self):
        self.ds = xr.open_dataset(self.filename)
        self.df = self.ds.to_dataframe()
        if self.qcflag == 1:
            QC = np.where(self.df["QC_FLAG"] == self.qcflag)[0]
        elif len(self.qcflag) == 2:
            QC = np.where(
                (self.df["QC_FLAG"] == self.qcflag[0])
                | (self.df["QC_FLAG"] == self.qcflag[1])
            )[0]
        self.df = self.df.iloc[QC]
        if self.upcast:
            self.df = extract_upcast(self.df)
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
        self.depths = self.df["DEPTH"].values
        self.temperatures = self.df["TEMPERATURE"].values + 273.15
        self.output_filename = self.filename[0:-3] + ".bufr"
        self.profile_name = self.filename.split("_")[-2]

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
        # First number is the number of directions, second number is the number of measurements
        codes_set_array(
            ibufr, "inputExtendedDelayedDescriptorReplicationFactor", [len(self.df)]
        )
        codes_set_array(
            ibufr,
            "unexpandedDescriptors",
            [
                201129,
                1087,
                201000,
                1019,
                1036,
                2148,
                1085,
                1086,
                8021,
                301011,
                301013,
                301021,
                11104,
                2169,
                11002,
                11001,
                2169,
                22032,
                22005,
                301011,
                301013,
                8021,
                4025,
                301021,
                22031,
                22004,
                8021,
                5068,
                1079,
                123000,
                31001,
                22056,
                120000,
                31002,
                301011,
                301013,
                301021,
                8080,
                33050,
                7062,
                8080,
                33050,
                22065,
                8080,
                33050,
                22045,
                8080,
                33050,
                22066,
                8080,
                33050,
                22064,
                8080,
                33050,
            ],
        )
        # Create the structure of the data section
        codes_set(ibufr, "observingPlatformManufacturerModel", "Mangopare")
        codes_set(
            ibufr,
            "observingPlatformManufacturerSerialNumber",
            self.ds.deck_unit_serial_number,
        )
        codes_set(ibufr, "#1#timeSignificance", 25)
        codes_set(ibufr, "#1#year", int(self.years[-1]))
        codes_set(ibufr, "#1#month", int(self.months[-1]))
        codes_set(ibufr, "#1#day", int(self.days[-1]))
        codes_set(ibufr, "#1#hour", int(self.hours[-1]))
        codes_set(ibufr, "#1#minute", int(self.minutes[-1]))
        codes_set(ibufr, "#1#latitude", self.latitudes[-1])
        codes_set(ibufr, "#1#longitude", self.longitudes[-1])
        codes_set(ibufr, "#2#year", int(self.years[-1]))
        codes_set(ibufr, "#2#month", int(self.months[-1]))
        codes_set(ibufr, "#2#day", int(self.days[-1]))
        codes_set(ibufr, "#2#hour", int(self.hours[-1]))
        codes_set(ibufr, "#2#minute", int(self.minutes[-1]))
        codes_set(ibufr, "#2#timeSignificance", 2)
        codes_set(ibufr, "#1#timePeriod", 50)
        codes_set(ibufr, "#2#latitude", self.latitudes[-1])
        codes_set(ibufr, "#2#longitude", self.longitudes[-1])
        codes_set(ibufr, "#1#uniqueIdentifierForProfile", self.profile_name)
        if self.upcast:
            codes_set(ibufr, "#1#directionOfProfile", 0)
        else:
            codes_set(ibufr, "#1#directionOfProfile", 3)  # CODE-Table 3-> Missing value
        #####################################
        #########Section 4, Data ############
        #####################################
        for count, i in enumerate(range(0, len(self.df) * 6, 6)):
            key1 = "#" + str(i + 1) + "#QualifierForGTSPPQualityFlag"
            key2 = "#" + str(i + 2) + "#QualifierForGTSPPQualityFlag"
            key3 = "#" + str(i + 3) + "#QualifierForGTSPPQualityFlag"
            key4 = "#" + str(i + 4) + "#QualifierForGTSPPQualityFlag"
            key5 = "#" + str(i + 5) + "#QualifierForGTSPPQualityFlag"
            key6 = "#" + str(i + 6) + "#QualifierForGTSPPQualityFlag"
            key1G = "#" + str(i + 1) + "#GlobalGTSPPQualityFlag"
            key2G = "#" + str(i + 2) + "#GlobalGTSPPQualityFlag"
            key3G = "#" + str(i + 3) + "#GlobalGTSPPQualityFlag"
            key4G = "#" + str(i + 4) + "#GlobalGTSPPQualityFlag"
            key5G = "#" + str(i + 5) + "#GlobalGTSPPQualityFlag"
            key6G = "#" + str(i + 6) + "#GlobalGTSPPQualityFlag"
            lat_key = "#" + str(count + 3) + "#latitude"
            lon_key = "#" + str(count + 3) + "#longitude"
            depth_key = "#" + str(count + 1) + "#depthBelowWaterSurface"
            pressure_key = "#" + str(count + 1) + "#oceanographicWaterPressure"
            temp_key = "#" + str(count + 1) + "#oceanographicWaterTemperature"
            cond_key = "#" + str(count + 1) + "#oceanographicWaterConductivity"
            salt_key = "#" + str(count + 1) + "#salinity"
            year_key = "#" + str(count + 3) + "#year"
            month_key = "#" + str(count + 3) + "#month"
            day_key = "#" + str(count + 3) + "#day"
            hour_key = "#" + str(count + 3) + "#hour"
            minute_key = "#" + str(count + 3) + "#minute"
            codes_set(ibufr, year_key, int(self.years[count]))
            codes_set(ibufr, month_key, int(self.months[count]))
            codes_set(ibufr, day_key, int(self.days[count]))
            codes_set(ibufr, hour_key, int(self.hours[count]))
            codes_set(ibufr, minute_key, int(self.minutes[count]))
            codes_set(ibufr, lon_key, self.longitudes[count])
            codes_set(ibufr, lat_key, self.latitudes[count])
            codes_set(ibufr, key1, 20)
            codes_set(ibufr, key1G, 9)
            codes_set(ibufr, depth_key, self.depths[count])
            codes_set(ibufr, key2, 13)  # Depth Quality Flags
            codes_set(ibufr, key2G, 9)  # Depth Quality Flags
            codes_set(ibufr, pressure_key, self.pressures[count])
            codes_set(ibufr, key3, 10)  # Pressure Quality Flags
            codes_set(ibufr, key3G, 9)  # Pressure Quality Flags
            codes_set(ibufr, temp_key, self.temperatures[count])
            codes_set(ibufr, key4, 11)  # Temperature Quality Flags
            codes_set(ibufr, key4G, 9)  # Temperature Quality Flags
            codes_set_missing(ibufr, cond_key)
            codes_set(ibufr, key5, 63)  # Conductivity Quality Flags
            codes_set(ibufr, key5G, 15)
            codes_set_missing(ibufr, salt_key)
            codes_set(ibufr, key6, 63)  # Salinity Quality Flags/Missing data
            codes_set(ibufr, key6G, 15)  # Salinity Quality Flags/Missing data
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
