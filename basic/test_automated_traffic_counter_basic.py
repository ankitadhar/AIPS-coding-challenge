import unittest
from unittest.mock import patch, mock_open
from io import StringIO
import tempfile
import os
from datetime import datetime, timedelta

from basic.automated_traffic_counter_basic import (
    transform_data,
    calculate_traffic,
    get_date,
    get_daily_traffic,
    get_top_n_half_hours,
    next_ts,
    has_contiguous_records,
    get_contiguous_ninty_mins_traffic,
    main
)


class TestAutomatedTrafficCounter(unittest.TestCase):
    """Test cases for automated traffic counter functions."""

    def setUp(self):
        """Set up test data."""
        self.sample_data_dict = {
            "2021-12-01T05:00:00": 5,
            "2021-12-01T05:30:00": 12,
            "2021-12-01T06:00:00": 14,
            "2021-12-01T06:30:00": 15,
            "2021-12-01T07:00:00": 25,
            "2021-12-01T07:30:00": 46,
            "2021-12-01T08:00:00": 42,
            "2021-12-01T15:00:00": 9,
            "2021-12-01T15:30:00": 11,
            "2021-12-01T23:30:00": 0,
            "2021-12-05T09:30:00": 18,
            "2021-12-05T10:30:00": 15,
            "2021-12-05T11:30:00": 7,
            "2021-12-05T12:30:00": 6,
            "2021-12-05T13:30:00": 9,
            "2021-12-05T14:30:00": 11,
            "2021-12-05T15:30:00": 15,
            "2021-12-08T18:00:00": 33,
            "2021-12-08T19:00:00": 28,
            "2021-12-08T20:00:00": 25,
            "2021-12-08T21:00:00": 21,
            "2021-12-08T22:00:00": 16,
            "2021-12-08T23:00:00": 11,
            "2021-12-09T00:00:00": 4
        }

        self.sample_file_content = """2021-12-01T05:00:00 5
2021-12-01T05:30:00 12
2021-12-01T06:00:00 14
2021-12-01T06:30:00 15
2021-12-01T07:00:00 25
2021-12-01T07:30:00 46"""

    # Test cases for transform_data

    def test_transform_data(self):
        """Test transform_data function."""
        mock_file = StringIO(self.sample_file_content)
        result = transform_data(mock_file)
        
        expected = {
            "2021-12-01T05:00:00": 5,
            "2021-12-01T05:30:00": 12,
            "2021-12-01T06:00:00": 14,
            "2021-12-01T06:30:00": 15,
            "2021-12-01T07:00:00": 25,
            "2021-12-01T07:30:00": 46
        }
        
        self.assertEqual(result, expected)

    def test_transform_data_empty_file(self):
        """Test transform_data with empty file."""
        mock_file = StringIO("")
        result = transform_data(mock_file)
        self.assertEqual(result, {})

    def test_transform_data_single_line(self):
        """Test transform_data with single line."""
        mock_file = StringIO("2021-12-01T05:00:00 5")
        result = transform_data(mock_file)
        expected = {"2021-12-01T05:00:00": 5}
        self.assertEqual(result, expected)

    # Test cases for calculate_traffic

    def test_calculate_traffic(self):
        """Test calculate_traffic function."""
        result = calculate_traffic(self.sample_data_dict)
        expected = sum(self.sample_data_dict.values())  # 398
        self.assertEqual(result, expected)

    def test_calculate_traffic_empty_dict(self):
        """Test calculate_traffic with empty dictionary."""
        result = calculate_traffic({})
        self.assertEqual(result, 0)

    def test_calculate_traffic_single_entry(self):
        """Test calculate_traffic with single entry."""
        data = {"2021-12-01T05:00:00": 10}
        result = calculate_traffic(data)
        self.assertEqual(result, 10)

    # Test cases for get_date

    def test_get_date(self):
        """Test get_date function."""
        timestamp = "2021-12-01T05:00:00"
        result = get_date(timestamp)
        self.assertEqual(result, "2021-12-01")

    def test_get_date_different_timestamps(self):
        """Test get_date with different timestamps."""
        test_cases = [
            ("2021-12-01T05:00:00", "2021-12-01"),
            ("2021-12-31T23:59:59", "2021-12-31"),
            ("2020-01-01T00:00:00", "2020-01-01")
        ]
        
        for timestamp, expected in test_cases:
            with self.subTest(timestamp=timestamp):
                result = get_date(timestamp)
                self.assertEqual(result, expected)

    # Test cases for get_daily_traffic

    def test_get_daily_traffic(self):
        """Test get_daily_traffic function."""
        result = get_daily_traffic(self.sample_data_dict)
        
        expected = {
            "2021-12-01": 179,  # 5+12+14+15+25+46+42+9+11+0
            "2021-12-05": 81,   # 18+15+7+6+9+11+15
            "2021-12-08": 134,  # 33+28+25+21+16+11
            "2021-12-09": 4     # 4
        }
        
        self.assertEqual(result, expected)

    def test_get_daily_traffic_empty_dict(self):
        """Test get_daily_traffic with empty dictionary."""
        result = get_daily_traffic({})
        self.assertEqual(result, {})

    def test_get_daily_traffic_single_day(self):
        """Test get_daily_traffic with single day data."""
        data = {
            "2021-12-01T05:00:00": 5,
            "2021-12-01T05:30:00": 12
        }
        result = get_daily_traffic(data)
        expected = {"2021-12-01": 17}
        self.assertEqual(result, expected)

    def test_get_top_n_half_hours(self):
        """Test get_top_n_half_hours function."""
        result = get_top_n_half_hours(self.sample_data_dict, n=3)
        
        # Expected top 3: 46, 42, 33
        expected_values = [46, 42, 33]
        result_values = [item[1] for item in result]
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result_values, expected_values)

    def test_get_top_n_half_hours_default_n(self):
        """Test get_top_n_half_hours with default n=3."""
        result = get_top_n_half_hours(self.sample_data_dict)
        self.assertEqual(len(result), 3)

    def test_get_top_n_half_hours_n_larger_than_data(self):
        """Test get_top_n_half_hours when n is larger than data size."""
        small_data = {"2021-12-01T05:00:00": 5, "2021-12-01T05:30:00": 12}
        result = get_top_n_half_hours(small_data, n=5)
        self.assertEqual(len(result), 2)

    def test_get_top_n_half_hours_n_zero(self):
        """Test get_top_n_half_hours with n=0."""
        result = get_top_n_half_hours(self.sample_data_dict, n=0)
        self.assertEqual(len(result), 0)

    # Test cases for next_ts

    def test_next_ts(self):
        """Test next_ts function."""
        timestamp = "2021-12-01T05:00:00"
        result = next_ts(timestamp, 30)
        expected = "2021-12-01T05:30:00"
        self.assertEqual(result, expected)

    def test_next_ts_different_deltas(self):
        """Test next_ts with different time deltas."""
        timestamp = "2021-12-01T05:00:00"
        test_cases = [
            (30, "2021-12-01T05:30:00"),
            (60, "2021-12-01T06:00:00"),
            (90, "2021-12-01T06:30:00"),
            (120, "2021-12-01T07:00:00")
        ]
        
        for delta, expected in test_cases:
            with self.subTest(delta=delta):
                result = next_ts(timestamp, delta)
                self.assertEqual(result, expected)

    def test_next_ts_cross_day_boundary(self):
        """Test next_ts when crossing day boundary."""
        timestamp = "2021-12-01T23:30:00"
        result = next_ts(timestamp, 60)
        expected = "2021-12-02T00:30:00"
        self.assertEqual(result, expected)

    # Test cases for has_contiguous_records

    def test_has_contiguous_records_true(self):
        """Test has_contiguous_records when records exist."""
        # Create data with contiguous records
        data = {
            "2021-12-01T05:00:00": 5,
            "2021-12-01T05:30:00": 12,
            "2021-12-01T06:00:00": 14
        }
        result = has_contiguous_records("2021-12-01T05:00:00", data)
        self.assertTrue(result)

    def test_has_contiguous_records_false_missing_30min(self):
        """Test has_contiguous_records when 30min record is missing."""
        data = {
            "2021-12-01T05:00:00": 5,
            "2021-12-01T06:00:00": 14
        }
        result = has_contiguous_records("2021-12-01T05:00:00", data)
        self.assertFalse(result)

    def test_has_contiguous_records_false_missing_60min(self):
        """Test has_contiguous_records when 60min record is missing."""
        data = {
            "2021-12-01T05:00:00": 5,
            "2021-12-01T05:30:00": 12
        }
        result = has_contiguous_records("2021-12-01T05:00:00", data)
        self.assertFalse(result)

    # Test cases for get_contiguous_ninty_mins_traffic

    def test_get_contiguous_ninty_mins_traffic(self):
        """Test get_contiguous_ninty_mins_traffic function."""
        # Create data with some contiguous 90-minute intervals
        data = {
            "2021-12-01T05:00:00": 5,
            "2021-12-01T05:30:00": 12,
            "2021-12-01T06:00:00": 14,
            "2021-12-01T06:30:00": 15,
            "2021-12-01T07:00:00": 25,
            "2021-12-01T07:30:00": 46,
            "2021-12-01T08:00:00": 42
        }
        
        result = get_contiguous_ninty_mins_traffic(data)
        
        expected = {
            "2021-12-01T05:00:00": 31,  # 5 + 12 + 14
            "2021-12-01T05:30:00": 41,  # 12 + 14 + 15
            "2021-12-01T06:00:00": 54,  # 14 + 15 + 25
            "2021-12-01T06:30:00": 86,  # 15 + 25 + 46
            "2021-12-01T07:00:00": 113  # 25 + 46 + 42
        }
        
        self.assertEqual(result, expected)

    def test_get_contiguous_ninty_mins_traffic_no_contiguous(self):
        """Test get_contiguous_ninty_mins_traffic with no contiguous intervals."""
        data = {
            "2021-12-01T05:00:00": 5,
            "2021-12-01T06:00:00": 14,  # Missing 05:30:00
            "2021-12-01T07:30:00": 46   # Missing 06:30:00 and 07:00:00
        }
        
        result = get_contiguous_ninty_mins_traffic(data)
        self.assertEqual(result, {})

    def test_get_contiguous_ninty_mins_traffic_empty_dict(self):
        """Test get_contiguous_ninty_mins_traffic with empty dictionary."""
        result = get_contiguous_ninty_mins_traffic({})
        self.assertEqual(result, {})

    # Test cases for main function

    @patch('basic.automated_traffic_counter_basic.open', new_callable=mock_open, read_data="2021-12-01T05:00:00 5\n2021-12-01T05:30:00 12\n2021-12-01T06:00:00 14\n")
    @patch('sys.argv', ['basic.automated_traffic_counter_basic.py'])
    def test_main_default_file(self, mock_file):
        """Test main function with default file path."""
        with patch('builtins.print') as mock_print:
            main()
            mock_file.assert_called_once_with("./data.txt", "r")
            mock_print.assert_called()

    @patch('basic.automated_traffic_counter_basic.open', new_callable=mock_open, read_data="2021-12-01T05:00:00 5\n2021-12-01T05:30:00 12\n2021-12-01T06:00:00 14\n")
    @patch('sys.argv', ['basic.automated_traffic_counter_basic.py', '--inputfile', 'custom_data.txt'])
    def test_main_custom_file(self, mock_file):
        """Test main function with custom file path."""
        with patch('builtins.print') as mock_print:
            main()
            mock_file.assert_called_once_with("custom_data.txt", "r")
            mock_print.assert_called()

    # Test that main function outputs the least cars timestamp message.

    @patch('basic.automated_traffic_counter_basic.open', new_callable=mock_open, read_data="2021-12-01T05:00:00 5\n2021-12-01T05:30:00 12\n2021-12-01T06:00:00 14\n")
    @patch('sys.argv', ['basic.automated_traffic_counter_basic.py'])
    def test_main_least_cars_output(self, mock_file):
        """Test that main function outputs the least cars timestamp message."""
        with patch('builtins.print') as mock_print:
            main()
            
            # Check that the specific print statement from line 51 was called
            # The call should include the timestamp with least cars in 90 minutes
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            
            # Look for the specific message format from line 51
            least_cars_message_found = any(
                "Timestamp with least number of cars seen in next 90 minutes:" in str(call)
                for call in print_calls
            )
            
            self.assertTrue(least_cars_message_found, 
                           "Expected print statement not found in output")
            
            # Also verify the timestamp should be "2021-12-01T05:00:00" (the first timestamp with contiguous data)
            expected_message = "Timestamp with least number of cars seen in next 90 minutes: 2021-12-01T05:00:00"
            self.assertIn(expected_message, print_calls)

    def test_integration_workflow(self):
        """Integration test for the complete workflow."""
        # Create a temporary file with test data
        test_data = """2021-12-01T05:00:00 5
2021-12-01T05:30:00 12
2021-12-01T06:00:00 14
2021-12-08T18:00:00 33
2021-12-08T19:00:00 28"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(test_data)
            temp_file_path = temp_file.name
        
        try:
            # Test the complete workflow
            with open(temp_file_path, 'r') as f:
                data_dict = transform_data(f)
            
            # Verify transform_data
            self.assertEqual(len(data_dict), 5)
            self.assertEqual(data_dict["2021-12-01T05:00:00"], 5)
            
            # Verify calculate_traffic
            total = calculate_traffic(data_dict)
            self.assertEqual(total, 92)  # 5+12+14+33+28
            
            # Verify get_daily_traffic
            daily = get_daily_traffic(data_dict)
            self.assertEqual(daily["2021-12-01"], 31)  # 5+12+14
            self.assertEqual(daily["2021-12-08"], 61)  # 33+28
            
            # Verify get_top_n_half_hours
            top_3 = get_top_n_half_hours(data_dict, 3)
            self.assertEqual(len(top_3), 3)
            self.assertEqual(top_3[0][1], 33)  # Highest traffic
            
        finally:
            os.unlink(temp_file_path)


if __name__ == '__main__':
    unittest.main()
