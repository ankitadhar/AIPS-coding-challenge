import unittest
from unittest.mock import patch, mock_open, MagicMock
import tempfile
import os
from datetime import datetime, timedelta

from traffic_analyzer import TrafficAnalyzer
from model import TrafficRecord


class TestTrafficAnalyzer(unittest.TestCase):
    """Test cases for TrafficAnalyzer class."""

    def setUp(self):
        """Set up test data."""
        self.sample_file_content = """2021-12-01T05:00:00 5
2021-12-01T05:30:00 12
2021-12-01T06:00:00 14
2021-12-01T06:30:00 15
2021-12-01T07:00:00 25
2021-12-01T07:30:00 46
2021-12-01T08:00:00 42
2021-12-05T09:30:00 18
2021-12-05T10:30:00 15
2021-12-08T18:00:00 33"""

        self.expected_traffic_records = [
            TrafficRecord(timestamp="2021-12-01T05:00:00", car_count=5),
            TrafficRecord(timestamp="2021-12-01T05:30:00", car_count=12),
            TrafficRecord(timestamp="2021-12-01T06:00:00", car_count=14),
            TrafficRecord(timestamp="2021-12-01T06:30:00", car_count=15),
            TrafficRecord(timestamp="2021-12-01T07:00:00", car_count=25),
            TrafficRecord(timestamp="2021-12-01T07:30:00", car_count=46),
            TrafficRecord(timestamp="2021-12-01T08:00:00", car_count=42),
            TrafficRecord(timestamp="2021-12-05T09:30:00", car_count=18),
            TrafficRecord(timestamp="2021-12-05T10:30:00", car_count=15),
            TrafficRecord(timestamp="2021-12-08T18:00:00", car_count=33)
        ]

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_init_and_post_init(self, mock_file):
        """Test TrafficAnalyzer initialization and __post_init__ method."""
        mock_file.return_value.readlines.return_value = [
            "2021-12-01T05:00:00 5\n",
            "2021-12-01T05:30:00 12\n"
        ]
        
        analyzer = TrafficAnalyzer("test_file.txt")
        
        # Verify file was opened correctly
        mock_file.assert_called_once_with("test_file.txt", "r")
        
        # Verify data was transformed correctly
        self.assertEqual(len(analyzer.traffic_data), 2)
        self.assertEqual(analyzer.traffic_data[0].timestamp, "2021-12-01T05:00:00")
        self.assertEqual(analyzer.traffic_data[0].car_count, 5)
        self.assertEqual(analyzer.traffic_data[1].timestamp, "2021-12-01T05:30:00")
        self.assertEqual(analyzer.traffic_data[1].car_count, 12)

    def test_transform_data_with_real_temp_file(self):
        """Test _transform_data method with real temporary file."""
        test_data = """2021-12-01T05:00:00 5
2021-12-01T05:30:00 12
2021-12-01T06:00:00 14"""

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(test_data)
            temp_file_path = temp_file.name

        try:
            analyzer = TrafficAnalyzer(temp_file_path)
            
            self.assertEqual(len(analyzer.traffic_data), 3)
            self.assertEqual(analyzer.traffic_data[0].timestamp, "2021-12-01T05:00:00")
            self.assertEqual(analyzer.traffic_data[0].car_count, 5)
            self.assertEqual(analyzer.traffic_data[2].timestamp, "2021-12-01T06:00:00")
            self.assertEqual(analyzer.traffic_data[2].car_count, 14)
        finally:
            os.unlink(temp_file_path)

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_transform_data_empty_file(self, mock_file):
        """Test _transform_data with empty file."""
        mock_file.return_value.readlines.return_value = []
        
        analyzer = TrafficAnalyzer("empty_file.txt")
        
        self.assertEqual(len(analyzer.traffic_data), 0)
        self.assertEqual(analyzer.traffic_data, [])

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_calculate_traffic(self, mock_file):
        """Test calculate_traffic method."""
        mock_file.return_value.readlines.return_value = [
            "2021-12-01T05:00:00 5\n",
            "2021-12-01T05:30:00 12\n",
            "2021-12-03T06:00:00 14\n"
        ]
        
        analyzer = TrafficAnalyzer("test_file.txt")
        result = analyzer.calculate_traffic()
        
        self.assertEqual(result, 31)  # 5 + 12 + 14

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_calculate_traffic_empty_data(self, mock_file):
        """Test calculate_traffic with empty data."""
        mock_file.return_value.readlines.return_value = []
        
        analyzer = TrafficAnalyzer("empty_file.txt")
        result = analyzer.calculate_traffic()
        
        self.assertEqual(result, 0)

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_get_daily_traffic(self, mock_file):
        """Test get_daily_traffic method."""
        mock_file.return_value.readlines.return_value = [
            "2021-12-01T05:00:00 5\n",
            "2021-12-01T05:30:00 12\n",
            "2021-12-01T06:00:00 14\n",
            "2021-12-05T09:30:00 18\n",
            "2021-12-05T10:30:00 15\n"
        ]
        
        analyzer = TrafficAnalyzer("test_file.txt")
        result = analyzer.get_daily_traffic()
        
        expected = {
            "2021-12-01": 31,  # 5 + 12 + 14
            "2021-12-05": 33   # 18 + 15
        }
        
        self.assertEqual(result, expected)

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_get_daily_traffic_single_day(self, mock_file):
        """Test get_daily_traffic with single day data."""
        mock_file.return_value.readlines.return_value = [
            "2021-12-01T05:00:00 5\n",
            "2021-12-01T05:30:00 12\n"
        ]
        
        analyzer = TrafficAnalyzer("test_file.txt")
        result = analyzer.get_daily_traffic()
        
        expected = {"2021-12-01": 17}
        self.assertEqual(result, expected)

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_get_top_n_half_hours_default(self, mock_file):
        """Test get_top_n_half_hours with default n=3."""
        mock_file.return_value.readlines.return_value = [
            "2021-12-01T05:00:00 5\n",
            "2021-12-01T05:30:00 12\n",
            "2021-12-01T06:00:00 14\n",
            "2021-12-01T06:30:00 25\n",
            "2021-12-01T07:00:00 46\n"
        ]
        
        analyzer = TrafficAnalyzer("test_file.txt")
        result = analyzer.get_top_n_half_hours()
        
        # Should return top 3 in descending order: 46, 25, 14
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].car_count, 46)
        self.assertEqual(result[1].car_count, 25)
        self.assertEqual(result[2].car_count, 14)

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_get_top_n_half_hours_custom_n(self, mock_file):
        """Test get_top_n_half_hours with custom n."""
        mock_file.return_value.readlines.return_value = [
            "2021-12-01T05:00:00 5\n",
            "2021-12-01T05:30:00 12\n",
            "2021-12-01T06:00:00 14\n"
        ]
        
        analyzer = TrafficAnalyzer("test_file.txt")
        result = analyzer.get_top_n_half_hours(n=2)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].car_count, 14)
        self.assertEqual(result[1].car_count, 12)

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_get_top_n_half_hours_n_larger_than_data(self, mock_file):
        """Test get_top_n_half_hours when n is larger than available data."""
        mock_file.return_value.readlines.return_value = [
            "2021-12-01T05:00:00 5\n",
            "2021-12-01T05:30:00 12\n"
        ]
        
        analyzer = TrafficAnalyzer("test_file.txt")
        result = analyzer.get_top_n_half_hours(n=5)
        
        self.assertEqual(len(result), 2)  # Should return only available records

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_get_date(self, mock_file):
        """Test _get_date method."""
        mock_file.return_value.readlines.return_value = ["2021-12-01T05:00:00 5\n"]
        
        analyzer = TrafficAnalyzer("test_file.txt")
        
        # Test various timestamps
        test_cases = [
            ("2021-12-01T05:00:00", "2021-12-01"),
            ("2021-12-31T23:59:59", "2021-12-31"),
            ("2020-01-01T00:00:00", "2020-01-01")
        ]
        
        for timestamp, expected_date in test_cases:
            with self.subTest(timestamp=timestamp):
                result = analyzer._get_date(timestamp)
                self.assertEqual(result, expected_date)

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_next_ts(self, mock_file):
        """Test _next_ts method."""
        mock_file.return_value.readlines.return_value = ["2021-12-01T05:00:00 5\n"]
        
        analyzer = TrafficAnalyzer("test_file.txt")
        
        # Test various time deltas
        test_cases = [
            ("2021-12-01T05:00:00", 30, "2021-12-01T05:30:00"),
            ("2021-12-01T05:00:00", 60, "2021-12-01T06:00:00"),
            ("2021-12-01T05:30:00", 30, "2021-12-01T06:00:00"),
            ("2021-12-01T23:30:00", 60, "2021-12-02T00:30:00")  # Cross day boundary
        ]
        
        for timestamp, delta, expected in test_cases:
            with self.subTest(timestamp=timestamp, delta=delta):
                result = analyzer._next_ts(timestamp, delta)
                self.assertEqual(result, expected)

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_has_contiguous_records_true(self, mock_file):
        """Test _has_contiguous_records when contiguous records exist."""
        mock_file.return_value.readlines.return_value = [
            "2021-12-01T05:00:00 5\n",
            "2021-12-01T05:30:00 12\n",
            "2021-12-01T06:00:00 14\n",
            "2021-12-01T06:30:00 15\n"
        ]
        
        analyzer = TrafficAnalyzer("test_file.txt")
        
        # Index 0 should have contiguous records (05:00, 05:30, 06:00)
        result = analyzer._has_contiguous_records(0)
        self.assertTrue(result)
        
        # Index 1 should have contiguous records (05:30, 06:00, 06:30)
        result = analyzer._has_contiguous_records(1)
        self.assertTrue(result)

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_has_contiguous_records_false_not_enough_records(self, mock_file):
        """Test _has_contiguous_records when not enough records available."""
        mock_file.return_value.readlines.return_value = [
            "2021-12-01T05:00:00 5\n",
            "2021-12-01T05:30:00 12\n"
        ]
        
        analyzer = TrafficAnalyzer("test_file.txt")
        
        # Index 0 should return False (not enough records for 90-min window)
        result = analyzer._has_contiguous_records(0)
        self.assertFalse(result)
        
        # Index 1 should return False (out of bounds)
        result = analyzer._has_contiguous_records(1)
        self.assertFalse(result)

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_has_contiguous_records_false_non_contiguous(self, mock_file):
        """Test _has_contiguous_records when records are not contiguous."""
        mock_file.return_value.readlines.return_value = [
            "2021-12-01T05:00:00 5\n",
            "2021-12-01T06:00:00 12\n",  # Missing 05:30:00
            "2021-12-01T07:00:00 14\n"
        ]
        
        analyzer = TrafficAnalyzer("test_file.txt")
        
        result = analyzer._has_contiguous_records(0)
        self.assertFalse(result)

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_get_next_records(self, mock_file):
        """Test _get_next_records method."""
        mock_file.return_value.readlines.return_value = [
            "2021-12-01T05:00:00 5\n",
            "2021-12-01T05:30:00 12\n",
            "2021-12-01T06:00:00 14\n",
            "2021-12-01T06:30:00 15\n"
        ]
        
        analyzer = TrafficAnalyzer("test_file.txt")
        
        # Get next 3 records starting from index 0
        result = analyzer._get_next_records(0)
        
        expected = [
            TrafficRecord(timestamp="2021-12-01T05:00:00", car_count=5),
            TrafficRecord(timestamp="2021-12-01T05:30:00", car_count=12),
            TrafficRecord(timestamp="2021-12-01T06:00:00", car_count=14)
        ]
        
        self.assertEqual(result, expected)
        
        # Get next 3 records starting from index 1
        result = analyzer._get_next_records(1)
        
        expected = [
            TrafficRecord(timestamp="2021-12-01T05:30:00", car_count=12),
            TrafficRecord(timestamp="2021-12-01T06:00:00", car_count=14),
            TrafficRecord(timestamp="2021-12-01T06:30:00", car_count=15)
        ]
        
        self.assertEqual(result, expected)

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_get_contiguous_ninety_mins_traffic(self, mock_file):
        """Test _get_contiguous_ninety_mins_traffic method."""
        mock_file.return_value.readlines.return_value = [
            "2021-12-01T05:00:00 5\n",
            "2021-12-01T05:30:00 12\n",
            "2021-12-01T06:00:00 14\n",
            "2021-12-01T06:30:00 15\n",
            "2021-12-01T07:00:00 25\n"
        ]
        
        analyzer = TrafficAnalyzer("test_file.txt")
        result = analyzer._get_contiguous_ninety_mins_traffic()
        
        expected = [
            TrafficRecord(timestamp="2021-12-01T05:00:00", car_count=31, duration_mins=90),  # 5+12+14
            TrafficRecord(timestamp="2021-12-01T05:30:00", car_count=41, duration_mins=90),  # 12+14+15
            TrafficRecord(timestamp="2021-12-01T06:00:00", car_count=54, duration_mins=90)   # 14+15+25
        ]
        
        self.assertEqual(result, expected)

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_get_contiguous_ninety_mins_traffic_no_contiguous(self, mock_file):
        """Test _get_contiguous_ninety_mins_traffic with no contiguous intervals."""
        mock_file.return_value.readlines.return_value = [
            "2021-12-01T05:00:00 5\n",
            "2021-12-01T06:00:00 12\n",  # Missing 05:30:00
            "2021-12-01T07:30:00 14\n"  # Missing 06:30:00 and 07:00:00
        ]
        
        analyzer = TrafficAnalyzer("test_file.txt")
        result = analyzer._get_contiguous_ninety_mins_traffic()
        
        self.assertEqual(result, [])

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_least_cars_in_ninety_mins(self, mock_file):
        """Test least_cars_in_ninety_mins method."""
        mock_file.return_value.readlines.return_value = [
            "2021-12-01T05:00:00 5\n",
            "2021-12-01T05:30:00 12\n",
            "2021-12-01T06:00:00 14\n",
            "2021-12-01T06:30:00 15\n",
            "2021-12-01T07:00:00 25\n"
        ]
        
        analyzer = TrafficAnalyzer("test_file.txt")
        result = analyzer.least_cars_in_ninety_mins()
        
        # Should return the interval with least cars (5+12+14=31)
        expected = TrafficRecord(timestamp="2021-12-01T05:00:00", car_count=31, duration_mins=90)
        self.assertEqual(result, expected)

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_least_cars_in_ninety_mins_no_contiguous_intervals(self, mock_file):
        """Test least_cars_in_ninety_mins with no contiguous intervals."""
        mock_file.return_value.readlines.return_value = [
            "2021-12-01T05:00:00 5\n",
            "2021-12-01T06:00:00 12\n"  # Missing 05:30:00
        ]
        
        analyzer = TrafficAnalyzer("test_file.txt")
        result = analyzer.least_cars_in_ninety_mins()

        expected = TrafficRecord(timestamp="N/A", car_count=0, duration_mins=90)
        self.assertEqual(result, expected)

    def test_file_not_found_error(self):
        """Test TrafficAnalyzer behavior when file doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            TrafficAnalyzer("nonexistent_file.txt")

    @patch('traffic_analyzer.open', new_callable=mock_open)
    def test_invalid_data_format(self, mock_file):
        """Test TrafficAnalyzer behavior with invalid data format."""
        mock_file.return_value.readlines.return_value = [
            "invalid_timestamp abc\n",
            "2021-12-01T05:30:00 12\n"
        ]
        
        with self.assertRaises(ValueError):
            TrafficAnalyzer("test_file.txt")

    def test_integration_with_real_data(self):
        """Integration test with realistic data scenario."""
        test_data = """2021-12-01T05:00:00 5
2021-12-01T05:30:00 12
2021-12-01T06:00:00 14
2021-12-01T06:30:00 15
2021-12-01T07:00:00 25
2021-12-01T07:30:00 46
2021-12-05T09:30:00 18
2021-12-05T10:30:00 15
2021-12-08T18:00:00 33"""

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(test_data)
            temp_file_path = temp_file.name

        try:
            analyzer = TrafficAnalyzer(temp_file_path)
            
            # Test all methods work together
            total_traffic = analyzer.calculate_traffic()
            self.assertEqual(total_traffic, 183)  # Sum of all car counts
            
            daily_traffic = analyzer.get_daily_traffic()
            expected_daily = {
                "2021-12-01": 117,  # 5+12+14+15+25+46
                "2021-12-05": 33,   # 18+15
                "2021-12-08": 33    # 33
            }
            self.assertEqual(daily_traffic, expected_daily)
            
            top_3 = analyzer.get_top_n_half_hours(3)
            self.assertEqual(len(top_3), 3)
            self.assertEqual(top_3[0].car_count, 46)  # Highest
            
            # Test 90-min intervals
            ninety_min_intervals = analyzer._get_contiguous_ninety_mins_traffic()
            self.assertTrue(len(ninety_min_intervals) > 0)
            
            least_cars = analyzer.least_cars_in_ninety_mins()
            self.assertIsInstance(least_cars, TrafficRecord)
            self.assertEqual(least_cars.duration_mins, 90)
            
        finally:
            os.unlink(temp_file_path)


if __name__ == '__main__':
    unittest.main()
