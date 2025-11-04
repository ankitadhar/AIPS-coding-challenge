import unittest
from unittest.mock import patch
from io import StringIO

from model import TrafficRecord, TrafficAnalysisResult


class TestTrafficRecord(unittest.TestCase):
    """Test cases for TrafficRecord dataclass."""

    def test_traffic_record_creation_with_all_fields(self):
        """Test creating TrafficRecord with all fields specified."""
        record = TrafficRecord(
            timestamp="2021-12-01T05:00:00",
            car_count=15,
            duration_mins=90
        )
        
        self.assertEqual(record.timestamp, "2021-12-01T05:00:00")
        self.assertEqual(record.car_count, 15)
        self.assertEqual(record.duration_mins, 90)

    def test_traffic_record_creation_with_default_duration(self):
        """Test creating TrafficRecord with default duration_mins."""
        record = TrafficRecord(
            timestamp="2021-12-01T05:30:00",
            car_count=25
        )
        
        self.assertEqual(record.timestamp, "2021-12-01T05:30:00")
        self.assertEqual(record.car_count, 25)
        self.assertEqual(record.duration_mins, 30)  # Default value    

    def test_traffic_record_field_types(self):
        """Test TrafficRecord field types."""
        record = TrafficRecord("2021-12-01T05:00:00", 15, 30)
        
        self.assertIsInstance(record.timestamp, str)
        self.assertIsInstance(record.car_count, int)
        self.assertIsInstance(record.duration_mins, int)


class TestTrafficAnalysisResult(unittest.TestCase):
    """Test cases for TrafficAnalysisResult dataclass."""

    def setUp(self):
        """Set up test data."""
        self.sample_traffic_records = [
            TrafficRecord("2021-12-01T07:30:00", 46),
            TrafficRecord("2021-12-01T08:00:00", 42),
            TrafficRecord("2021-12-08T18:00:00", 33)
        ]
        
        self.sample_daily_traffic = {
            "2021-12-01": 179,
            "2021-12-05": 81,
            "2021-12-08": 134
        }
        
        self.sample_least_ninety_mins = TrafficRecord(
            "2021-12-01T05:00:00", 31, 90
        )

    def test_traffic_analysis_result_creation(self):
        """Test creating TrafficAnalysisResult with all fields."""
        result = TrafficAnalysisResult(
            total_traffic=398,
            daily_traffic=self.sample_daily_traffic,
            top_n_half_hours=self.sample_traffic_records,
            least_ninety_mins_traffic=self.sample_least_ninety_mins
        )
        
        self.assertEqual(result.total_traffic, 398)
        self.assertEqual(result.daily_traffic, self.sample_daily_traffic)
        self.assertEqual(result.top_n_half_hours, self.sample_traffic_records)
        self.assertEqual(result.least_ninety_mins_traffic, self.sample_least_ninety_mins)

    def test_traffic_analysis_result_custom_repr(self):
        """Test TrafficAnalysisResult custom __repr__ method."""
        result = TrafficAnalysisResult(
            total_traffic=398,
            daily_traffic=self.sample_daily_traffic,
            top_n_half_hours=self.sample_traffic_records,
            least_ninety_mins_traffic=self.sample_least_ninety_mins
        )
        
        repr_output = repr(result)
        
        # Check that the custom repr is used (contains expected sections)
        self.assertIn("Calculating total traffic...", repr_output)
        self.assertIn("The number of cars seen in total: 398", repr_output)
        self.assertIn("Calculating daily traffic...", repr_output)
        self.assertIn("Finding top 3 half hours with highest traffic...", repr_output)
        self.assertIn("Finding contiguous 90 minutes intervals car counts...", repr_output)

    def test_traffic_analysis_result_str_representation(self):
        """Test TrafficAnalysisResult string representation (should use custom __repr__)."""
        result = TrafficAnalysisResult(
            total_traffic=100,
            daily_traffic={"2021-12-01": 100},
            top_n_half_hours=[TrafficRecord("2021-12-01T05:00:00", 50)],
            least_ninety_mins_traffic=TrafficRecord("2021-12-01T05:00:00", 75, 90)
        )
        
        str_output = str(result)
        
        # str() should use the custom __repr__ method
        self.assertIn("The number of cars seen in total: 100", str_output)
        self.assertIn("2021-12-01\t100", str_output)
        self.assertIn("2021-12-01T05:00:00 50", str_output)
        self.assertIn("Timestamp with least number of cars seen in next 90 minutes: 2021-12-01T05:00:00", str_output)

    def test_traffic_analysis_result_repr_daily_traffic_section(self):
        """Test daily traffic section in __repr__ output."""
        daily_traffic = {
            "2021-12-01": 179,
            "2021-12-05": 81
        }
        
        result = TrafficAnalysisResult(
            total_traffic=260,
            daily_traffic=daily_traffic,
            top_n_half_hours=[],
            least_ninety_mins_traffic=self.sample_least_ninety_mins
        )
        
        repr_output = repr(result)
        
        self.assertIn("Calculating daily traffic...", repr_output)
        self.assertIn("Date       Number of cars seen", repr_output)
        self.assertIn("-------------------------------", repr_output)
        self.assertIn("2021-12-01\t179", repr_output)
        self.assertIn("2021-12-05\t81", repr_output)

    def test_traffic_analysis_result_repr_top_half_hours_section(self):
        """Test top half hours section in __repr__ output."""
        top_records = [
            TrafficRecord("2021-12-01T07:30:00", 46),
            TrafficRecord("2021-12-01T08:00:00", 42)
        ]
        
        result = TrafficAnalysisResult(
            total_traffic=88,
            daily_traffic={},
            top_n_half_hours=top_records,
            least_ninety_mins_traffic=self.sample_least_ninety_mins
        )
        
        repr_output = repr(result)
        
        self.assertIn("Finding top 3 half hours with highest traffic...", repr_output)
        self.assertIn("Timestamp           Number of cars seen", repr_output)
        self.assertIn("---------------------------------------", repr_output)
        self.assertIn("2021-12-01T07:30:00 46", repr_output)
        self.assertIn("2021-12-01T08:00:00 42", repr_output)

    def test_traffic_analysis_result_repr_ninety_mins_section(self):
        """Test 90 minutes section in __repr__ output."""
        least_ninety = TrafficRecord("2021-12-01T05:00:00", 31, 90)
        
        result = TrafficAnalysisResult(
            total_traffic=100,
            daily_traffic={},
            top_n_half_hours=[],
            least_ninety_mins_traffic=least_ninety
        )
        
        repr_output = repr(result)
        
        self.assertIn("Finding contiguous 90 minutes intervals car counts...", repr_output)
        self.assertIn("Timestamp with least number of cars seen in next 90 minutes: 2021-12-01T05:00:00", repr_output)

    def test_traffic_analysis_result_field_types(self):
        """Test TrafficAnalysisResult field types."""
        result = TrafficAnalysisResult(
            total_traffic=398,
            daily_traffic=self.sample_daily_traffic,
            top_n_half_hours=self.sample_traffic_records,
            least_ninety_mins_traffic=self.sample_least_ninety_mins
        )
        
        self.assertIsInstance(result.total_traffic, int)
        self.assertIsInstance(result.daily_traffic, dict)
        self.assertIsInstance(result.top_n_half_hours, list)
        self.assertIsInstance(result.least_ninety_mins_traffic, TrafficRecord)

    def test_traffic_analysis_result_field_modification(self):
        """Test modifying TrafficAnalysisResult fields."""
        result = TrafficAnalysisResult(
            total_traffic=398,
            daily_traffic=self.sample_daily_traffic,
            top_n_half_hours=self.sample_traffic_records,
            least_ninety_mins_traffic=self.sample_least_ninety_mins
        )
        
        # Modify fields
        result.total_traffic = 500
        result.daily_traffic = {"2021-12-10": 500}
        result.top_n_half_hours = [TrafficRecord("2021-12-10T10:00:00", 100)]
        result.least_ninety_mins_traffic = TrafficRecord("2021-12-10T09:00:00", 200, 90)
        
        self.assertEqual(result.total_traffic, 500)
        self.assertEqual(result.daily_traffic, {"2021-12-10": 500})
        self.assertEqual(result.top_n_half_hours, [TrafficRecord("2021-12-10T10:00:00", 100)])
        self.assertEqual(result.least_ninety_mins_traffic, TrafficRecord("2021-12-10T09:00:00", 200, 90))

    def test_traffic_analysis_result_repr_integration(self):
        """Integration test for complete __repr__ output format."""
        daily_traffic = {
            "2021-12-01": 179,
            "2021-12-05": 81
        }
        
        top_records = [
            TrafficRecord("2021-12-01T07:30:00", 46),
            TrafficRecord("2021-12-01T08:00:00", 42),
            TrafficRecord("2021-12-08T18:00:00", 33)
        ]
        
        least_ninety = TrafficRecord("2021-12-01T05:00:00", 31, 90)
        
        result = TrafficAnalysisResult(
            total_traffic=260,
            daily_traffic=daily_traffic,
            top_n_half_hours=top_records,
            least_ninety_mins_traffic=least_ninety
        )
        
        repr_output = repr(result)
        
        # Verify the complete output structure
        lines = repr_output.split('\n')
        
        # Should have multiple sections with proper formatting
        self.assertTrue(any("Calculating total traffic..." in line for line in lines))
        self.assertTrue(any("260" in line for line in lines))
        self.assertTrue(any("Calculating daily traffic..." in line for line in lines))
        self.assertTrue(any("2021-12-01\t179" in line for line in lines))
        self.assertTrue(any("Finding top 3 half hours" in line for line in lines))
        self.assertTrue(any("2021-12-01T07:30:00 46" in line for line in lines))
        self.assertTrue(any("Finding contiguous 90 minutes" in line for line in lines))
        self.assertTrue(any("2021-12-01T05:00:00" in line for line in lines))

    def test_traffic_analysis_result_print_output(self):
        """Test TrafficAnalysisResult when printed (uses __repr__)."""
        result = TrafficAnalysisResult(
            total_traffic=100,
            daily_traffic={"2021-12-01": 100},
            top_n_half_hours=[TrafficRecord("2021-12-01T05:00:00", 50)],
            least_ninety_mins_traffic=TrafficRecord("2021-12-01T05:00:00", 75, 90)
        )
        
        # Capture print output
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            print(result)
            printed_output = mock_stdout.getvalue()
        
        # Should contain the formatted output
        self.assertIn("The number of cars seen in total: 100", printed_output)
        self.assertIn("2021-12-01\t100", printed_output)
        self.assertIn("2021-12-01T05:00:00 50", printed_output)

if __name__ == '__main__':
    unittest.main()
