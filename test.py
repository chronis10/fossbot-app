import unittest
from unittest.mock import MagicMock, patch
import bluetooth_device
import utils

class TestBluetoothFunctions(unittest.TestCase):

    @patch('utils._run_bt_command')
    def test_pair_device_success(self, mock_run_bt_command):
        mock_run_bt_command.return_value = ('Pairing successful', None)
        ok, msg = utils.pair_device('00:11:22:33:44:55')
        self.assertTrue(ok)
        self.assertEqual(msg, 'Paired!')

    @patch('utils._run_bt_command')
    def test_pair_device_failure(self, mock_run_bt_command):
        mock_run_bt_command.return_value = ('Failed to pair', None)
        ok, msg = utils.pair_device('00:11:22:33:44:55')
        self.assertFalse(ok)
        self.assertIn('Failed to pair', msg)

    @patch('utils._run_bt_command')
    def test_connect_device_success(self, mock_run_bt_command):
        mock_run_bt_command.return_value = ('Connection successful', None)
        ok, msg = utils.connect_device('00:11:22:33:44:55')
        self.assertTrue(ok)
        self.assertEqual(msg, 'Connected!')

    @patch('utils._run_bt_command')
    def test_connect_device_failure(self, mock_run_bt_command):
        mock_run_bt_command.return_value = ('Connection failed', None)
        ok, msg = utils.connect_device('00:11:22:33:44:55')
        self.assertFalse(ok)
        self.assertIn('Connection failed', msg)

    @patch('utils._run_bt_command')
    def test_trust_device_success(self, mock_run_bt_command):
        mock_run_bt_command.return_value = ('trust succeeded', None)
        ok, msg = utils.trust_device('00:11:22:33:44:55')
        self.assertTrue(ok)
        self.assertEqual(msg, 'Trusted!')

    @patch('utils._run_bt_command')
    def test_trust_device_failure(self, mock_run_bt_command):
        mock_run_bt_command.return_value = ('Trust failed', None)
        ok, msg = utils.trust_device('00:11:22:33:44:55')
        self.assertFalse(ok)
        self.assertIn('Trust failed', msg)

if __name__ == '__main__':
    unittest.main()