[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
# Encoding Mangōpare sensors using ECCODES

## Installation
This installs the eccodes libraries and additional libraries needed such as numpy, pandas, xarray

`pip install -r requirements/default.txt`

`python setup.py install`

## Example
``` python
from GTS_encode import GTS_encode_subfloat, GTS_encode_ship, GTS_encode_glider

file = "../test/MOANA_0058_434_230228081912_qc.nc"
centre_code = 69 # MetService Centre code from table Code Table C-11 69 -> Wellington (RSMC)
GTS=GTS_encode_subfloat(file, centre_code, upcast=True) #upcast True if only upcast is needed
```
or 
```python
GTS= GTS_encode_ship(file, centre_code, upcast=True)
```
or 
```python
GTS= GTS_encode_glider(file, centre_code, upcast=True)
```
```python
GTS.run()
``` 
---
## Encoding support for mangōpare sensors.

This encoding uses the toolbox developed by eccodes and it is adapted to encode mangōpare sensors using the template for Temperature and salinity profile observed by profile floats (315003) and the template to represent data derived from a ship based lowered instrument measuring subsurface seawater temperature, salinity and current profiles (315007).

## Index
### utils
Useful functions to support the encoding of mangōpare sensors
- **[inflection_data](https://github.com/metocean/moana-bufrtools/blob/39d17562c6e5e6bf30dc7769a4517b78a33e7eb8/GTS_encode/utils.py#L13)** - Identification of inflection points
- **[extract_upcast](https://github.com/metocean/moana-bufrtools/blob/39d17562c6e5e6bf30dc7769a4517b78a33e7eb8/GTS_encode/utils.py#L26)** - Extraction of upcast measurements
- **[pres](https://github.com/metocean/moana-bufrtools/blob/39d17562c6e5e6bf30dc7769a4517b78a33e7eb8/GTS_encode/utils.py#L38)** - conversion of depth (m) to pressure (Pa)

### GTS_encode
Includes classes to encode the data into GTS/BUFR format. This codes are tailored for Mangōpare sensors format, changes might be needed if the format changes, but it should be straightforward. 

There are three classes: 
- **[GTS_encode_subfloat](https://github.com/metocean/moana-bufrtools/blob/39d17562c6e5e6bf30dc7769a4517b78a33e7eb8/GTS_encode/GTS_encode.py#L21)**
- **[GTS_encode_ship](https://github.com/metocean/moana-bufrtools/blob/39d17562c6e5e6bf30dc7769a4517b78a33e7eb8/GTS_encode/GTS_encode.py#L154)**
- **[GTS_encode_glider](https://github.com/metocean/moana-bufrtools/blob/39d17562c6e5e6bf30dc7769a4517b78a33e7eb8/GTS_encode/GTS_encode.py#L376)**
---
### GTS_encode_subfloat 
- **Category 15** – Oceanographic report sequence 
- **Sequence 003** – Temperature and salinity profile observed by profile floats
The template includes the following items 

|315003 | Subsurface float Template|
| :------------- | :------------- |
|301011| Time |
|005001| Latitude|
|006001| Longitude|
|008080| Qualifier for GTSPP Quality Flag|
|033050| Global GTSPP Quality Flag|
|007065| Water Pressure (Pa)|
|008080| Qualifier for GTSPP Quality Flag|
|033050| Global GTSPP Quality Flag|
|022045| Oceanographic Water Temperature (K)|


### GTS_encode_ship
- **Category 15** – Oceanographic report sequence 
- **Sequence 007** – Representation of data derived from a ship based lowered instrument measuring subsurface seawater temperature, salinity and current profiles
The Template includes the following items

|315003 | Ship Template|
| :------------- | :------------- |
|301003 | Ship's call sign and motion|
||**Extended identification** |
|001019 | Long station or site name |
|001103 | IMO Number|
|001087 | WMO marine observing platflorm extended identifier |
|| **Cruise/ship line information**  |
|001036 | Agency in chage of operating the observing platform|
|001115 | Identifier of the cruise or mission under which the data were collected|
|001080 | Ship line number according to SOOP|
|005036 | Ship transect number according to SOOP|
|301011 | Year, month, day|
|301012 | Hour, minute|
|301021 | Latitude/Longitude (high accuracy)|
||**Profile Information**|
|001079 | Unique identifier for the profile|
|001023 | Observation sequence number|
|022063 | Total water depth|
||**Surface Pressure**|
|101000 | Delayed replication of 1 descriptor|
|031000 | Short delayed descriptor replication factor|
|302001 | Pressure and 3-hour pressure change|
||**Waves**|
|101000 | Delayed replication of 1 descriptor|
|031000 | Short delayed descriptor replication factor|
|302021 | Waves|
||**Temperature and humidity data**|
|101000 | Delayed replication of 1 descriptor |
|031000 | Short delayed descriptor replication factor |
|302052 | Ship temperature and humidity data|
||**Wind data**|
|101000 | Delayed replication of 1 descriptor|
|031000 | Short delayed descriptor replication factor|
|302059 | Ship wind data    |
||**Surface temperature, salinity and current**|
|022067 | Instrument type for water temperature/salinity profile measurement|
|002171 | Instrument serial number for water temperature profile measurement|
|302090 | Sea/water temperature high precision (surface)|
|306033 | Surface salinity|
|306034 | Surface current  |
|002171 | Instrument serial number for water temperature profile measurement (set to missing)|
|022067 | Instrument type for water temperature/salinity profile measurement (set to missing)|
||**Temperature and salinity profile data**|
|002038 | Method of water temperature and/or salinity measurement|
|022067 | Instrument type for water temperature /salinity profile measurement|
|022068 | Water temperature profile recorder types|
|002171 | Instrument serial number for water temperature profile measurement|
|002033 | Method of salinity/depth measurement|
|002032 | Indicator for digitization|
|022056 | Direction of profile|
|003011 | Method of depth calculation |
|306035 | Temperature and salinity profile|
||**Current profile data**|
|107000 | Delayed replication of 7 descriptors|
|031000 | Short delayed descriptor replication factor|
|002032 | Indicator for digitization|
|003010 | Method of sea/water current measurement|
|002031 | Duration and time of current measurement|
|002040 | Method of removing velocity and motion of platform from current|
|022056 | Direction of profile|
|003011 | Method of depth calculation|
|306036 | Current profile|
||**Dissolved oxygen profile data**|
|104000 | Delayed replication of 4 descriptors|
|031000 | Short delayed descriptor replication factor|
|002032 | Indicator for digitization|
|003012 | Instrument type/sensor for dissolved oxygen measurement|
|003011 | Method of depth calculation   |     
|306037 | Dissolved oxygen profile data|

### GTS_encode_glider
The [glider template](https://github.com/wmo-im/BUFR4/issues/16) is a work in process, here is the latest version **Not approved yet**:
- **Category 15** – Oceanographic report sequence 
- **Sequence 012** – observations from a single glider trajectory profile

The Template includes the following items
|315012 | Glider Template|
| :------------- | :------------- |
||**Identification** |
|301150 	|(WIGOS identifier) 	|
|201129 	|Change data width 	Increase width of following elements by 1 bit|
|001087 	|WMO marine observing platform extended identifier 	|
|201000 	|Change data width 	Cancel increase in width|
|001019 	|Long station or site name 	|
|001036 	|Agency in charge of operating the observing platform 	|
|002148 	|Data collection and/or location system 	|
|001085 	|Observing platform manufacturer's model 	|
|001086 	|Observing platform manufacturer's serial number | 	
||**Surface Pressure**|
|008021 	|Time significance 	Set to 25, nominal reporting time|
|301011 	|(Year, month, day) 	|
|301013 	|(Hour, minute, second) |	
|301021 	|(Latitude / longitude (high accuracy)) | 	
|011104 	|True heading of aircraft, ship or other mobile platform | 	
|002169 	|Anemometer type 	Set to 2, wind observation through ambient noise (WOTAN)|
|011002 	|Wind speed 	|
|011001 	|Wind direction |	
|002169 	|Anemometer type 	Set to missing / cancel previous value|
||**Ocean Currents**|
|022032 	|Speed of sea surface current 	|
|022005 	|Direction of sea-surface current| 	
|301011 	|(Year, month, day) 	|
|301013 	|(Hour, minute, second) |	
|008021 	|Time significance 	Set to 2, time averaged |
|004025 	|Time period or displacement 	Duration of dive |
|301021 	|(Latitude / longitude (high accuracy)) 	|
|022031 	|Speed of current 	|
|022004 	|Direction of current| 	
|008021 	|Time significance 	Set to missing / cancel previous value|
|005068 	|Profile number 	|
|001079 	|Unique identifier for profile 	|
||**Profile sections**|
|126000 	|Delayed replication of 26 descriptors| 	
|031001 	|Delayed descriptor replication factor 	Number of profile sections (e.g. descending, horizontal, ascending)|
|022056 	|Direction of profile 	0 (ascending / upwards profile), 1 (descending / downwards profile), or 2 (horizontal)|
|123000 	|Delayed replication of 23 descriptors 	|
|031002 	|Extended delayed descriptor replication factor| 	
|301011 	|Year, month, day 	|
|301013 	|Hour, minute, second |	
|301021 	|Latitude / Longitude (high accuracy) 	|
|008080 	|Qualifier for GTSPP quality flag 	20, position |
|033050 	|Global GTSPP quality flag 	|
|007062 	|Depth below water surface 	|
|008080 	|Qualifier for GTSPP quality flag 	13, water depth at a level |
|033050 	|Global GTSPP quality flag 	|
|022065 	|Water pressure 	|
|008080 	|Qualifier for GTSPP quality flag 	10, water pressure at a level |
|033050 	|Global GTSPP quality flag 	|
|022045 	|Sea/water temperature 	|
|008080 	|Qualifier for GTSPP quality flag 	11, water temperature at a level |
|033050 	|Global GTSPP quality flag 	|
|022066 	|Water conductivity 	|
|008080 	|Qualifier for GTSPP quality flag 	25, water conductivity at a level |
|033050 	|Global GTSPP quality flag 	|
|022064 	|Salinity 	|
|008080 	|Qualifier for GTSPP quality flag 	12, salinity at a level |
|033050 	|Global GTSPP quality flag 	|
|042016 	|Sea water potential density referenced to sea surface 	|
|008080 	|Qualifier for GTSPP quality flag 	26, sea water potential density at a level |
|033050 	|Global GTSPP quality flag |

---

### Notes 
- Mangōpare sensor has the depth in meters - this is converted to dbars then to Pa.
- Mangōpare provides the temperature in Celsius - this is converted to Kelvin.

---
## Licensing
Please see LICENSE.md for the license under which this code can be shared.  Please consider contributing to the code under this repository whenever possible rather then forking or cloning into a new repository so all can benefit from collaborative work.  If you need to fork/clone into a new repository, please let us know so we can include any new developments as a community.

---
## Attribution Statement
Original code base by MetOcean Solutions, a Division of Meteorological Service of New Zealand Ltd, developed as part of the Moana Project. The Moana Project is funded by the New Zealand Ministry of Business, Innovation, and Employment (MBIE) Endeavour Fund.

Contributors to the current version in include: MetOcean Solutions, Berring Data Collective

The Mangōpare sensor and deck unit hardware were developed by Zebra-Tech, Ltd, Nelson, New Zealand as part of the Moana Project.  Sensors are available through https://www.zebra-tech.co.nz/

---
## Community
A fishing vessel, in-situ ocean observing quality control working group is in development through FVON (https://fvon.org/).  Please contact either the Moana Project (info@moanaproject.org) or FVON (through their website) for more information.

---
