import unittest
import os
from unittest.mock import patch
from datetime import datetime
from wrapper import Wrapper

class TestWrapper(unittest.TestCase):

    def setUp(self):
        self.filelist = [
            "/path/to/file1.nc",
            "/path/to/file2.nc",
            "/path/to/file3.nc"
        ]
        self.out_dir = "/path/to/output"
        self.GTS_template = "GTS_encode_ship"
        self.centre_code = 69
        self.logger = None
        self.wrapper = Wrapper(
            filelist=self.filelist,
            out_dir=self.out_dir,
            GTS_template=self.GTS_template,
            centre_code=self.centre_code,
            logger=self.logger
        )

    def test_available_for_GTS_publication(self):
        filename = "/path/to/file.nc"
        with patch("wrapper.xr.open_dataset") as mock_open_dataset:
            mock_open_dataset.return_value.attrs = {
                "public": True,
                "wigos_id": "123456",
                "publication_date": "01/01/2022"
            }
            mock_open_dataset.return_value.__getitem__.side_effect = [
                datetime(2022, 1, 1),
                datetime(2022, 1, 2)
            ]
            result = self.wrapper._available_for_GTS_publication(filename)
            self.assertTrue(result)

    def test_initialize_outdir(self):
        dir_path = "/path/to/output"
        with patch("wrapper.os.mkdir") as mock_mkdir:
            self.wrapper._initialize_outdir(dir_path)
            mock_mkdir.assert_called_once_with(dir_path)

    def test_set_filelist_with_success_files(self):
        success_files = [
            "/path/to/success1.nc",
            "/path/to/success2.nc"
        ]
        self.wrapper._success_files = success_files
        self.wrapper._set_filelist()
        self.assertEqual(self.wrapper.filelist, success_files)

    def test_set_filelist_without_success_files(self):
        self.wrapper._success_files = []
        self.wrapper._set_filelist()
        self.assertEqual(self.wrapper.filelist, [])

    @patch("wrapper.importlib.import_module")
    def test_run(self, mock_import_module):
        mock_GTS_encode = mock_import_module.return_value.GTS_encode_ship
        mock_GTS_encode.return_value.run.return_value = "/path/to/output/file.nc"
        self.wrapper._available_for_GTS_publication = lambda x: True
        result = self.wrapper.run()
        self.assertEqual(result["filelist"], ["/path/to/output/file.nc"])

if __name__ == "__main__":
    unittest.main()