import os
import unittest
import pytest
from mock import MagicMock
from unittest.mock import patch, mock_open

from GTS_encode.GTS_encode import GTS_encode_subfloat, GTS_encode_ship, GTS_encode_glider

class testinfo(object):
    file = "/source/moana-bufrtools/data/MOANA_0058_434_230228081912_qc.nc"
    centre_code = 69 # MetService Centre code from table Code Table C-11 69 -> Wellington (RSMC)

class Test_encoding(unittest.TestCase):
    def test_encode_subfloat(self):
        open_mock = mock_open()
        with patch("GTS_encode.GTS_encode_subfloat", open_mock, create=True):
            GTS=GTS_encode_subfloat(testinfo.file, testinfo.centre_code, upcast=True, QC_flag=1)
            GTS.run()
    
    def test_encode_ship(self):
        open_mock = mock_open()
        with patch("GTS_encode.GTS_encode_ship", open_mock, create=True):
            GTS=GTS_encode_ship(testinfo.file, testinfo.centre_code, upcast=True, QC_flag=1)
            GTS.run()

    def test_encode_glider(self):
        open_mock = mock_open()
        with patch("GTS_encode.GTS_encode_glider", open_mock, create=True):
            GTS=GTS_encode_glider(testinfo.file, testinfo.centre_code, upcast=True, QC_flag=1)
            GTS.run()



