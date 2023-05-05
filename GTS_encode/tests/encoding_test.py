from GTS_encode.GTS_encode import GTS_encode_subfloat, GTS_encode_ship, GTS_encode_glider

file = "../data/MOANA_0058_434_230228081912_qc.nc"
centre_code = 69 # MetService Centre code from table Code Table C-11 69 -> Wellington (RSMC)
GTS=GTS_encode_subfloat(file, centre_code, upcast=True, QC_flag=1) #upcast True if only upcast is needed
GTS.run()