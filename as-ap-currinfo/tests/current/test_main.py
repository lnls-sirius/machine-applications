#!/usr/bin/env python3.6

"""Module to test AS-AP-CurrInfo Current Soft IOC main module."""

import unittest
from unittest import mock
import siriuspy.util as util
from as_ap_currinfo.current.current import _PCASDriver
from as_ap_currinfo.current.main import App
import as_ap_currinfo.current.pvs as pvs


valid_interface = (
    'init_class',
    'driver',
    'process',
    'read',
    'write',
    'pvs_database'
)


class TestASAPCurrInfoCurrentMain(unittest.TestCase):
    """Test AS-AP-CurrInfo Current Soft IOC."""

    def setUp(self):
        """Initialize Soft IOC."""
        self.mock_driver = mock.create_autospec(_PCASDriver)
        pvs.select_ioc('si')
        App.init_class()
        printbanner_patcher = mock.patch(
            "as_ap_currinfo.current.pvs.print_banner_and_save_pv_list",
            autospec=True)
        self.addCleanup(printbanner_patcher.stop)
        self.mock_printbanner = printbanner_patcher.start()

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(App, valid_interface,
                                                      print_flag=True)
        self.assertTrue(valid)

    def test_write_DCCT_FltCheckOn(self):
        """Test write DCCT-Sel."""
        app = App(self.mock_driver)
        app.write('DCCT-Sel', 0)
        app.write('DCCT-Sel', 1)
        app.write('DCCT-Sel', 2)
        self.mock_driver.setParam.assert_not_called()

    def test_write_DCCTFltCheck(self):
        """Test write DCCTFltCheck-Sel."""
        app = App(self.mock_driver)
        app.write('DCCTFltCheck-Sel', 1)
        self.mock_driver.setParam.assert_called_with('DCCTFltCheck-Sts', 1)

    def test_write_DCCT_FltCheckOff(self):
        """Test write DCCT-Sel."""
        app = App(self.mock_driver)
        app.write('DCCTFltCheck-Sel', 1)
        app.write('DCCT-Sel', 1)
        self.mock_driver.setParam.assert_called_with('DCCT-Sts', 1)


if __name__ == "__main__":
    unittest.main()