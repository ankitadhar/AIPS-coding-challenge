import unittest
from unittest.mock import patch, mock_open, MagicMock
import tempfile
import os

from main import main
from model import TrafficRecord, TrafficAnalysisResult


class TestMain(unittest.TestCase):
    """Test cases for main.py functionality."""

    def setUp(self):
        """Set up test data."""
        self.sample_file_content = """2021-12-01T05:00:00 5
2021-12-01T05:30:00 12
2021-12-01T06:00:00 14
2021-12-01T06:30:00 15
2021-12-01T07:00:00 25
2021-12-01T07:30:00 46"""

        self.expected_traffic_records = [
            TrafficRecord(timestamp="2021-12-01T05:00:00", car_count=5),
            TrafficRecord(timestamp="2021-12-01T05:30:00", car_count=12),
            TrafficRecord(timestamp="2021-12-01T06:00:00", car_count=14),
            TrafficRecord(timestamp="2021-12-01T06:30:00", car_count=15),
            TrafficRecord(timestamp="2021-12-01T07:00:00", car_count=25),
            TrafficRecord(timestamp="2021-12-01T07:30:00", car_count=46)
        ]

    @patch('traffic_analyzer.open', new_callable=mock_open, read_data="2021-12-01T05:00:00 5\n2021-12-01T05:30:00 12\n2021-12-01T06:00:00 14\n")
    @patch('sys.argv', ['main.py'])
    def test_main_default_file(self, mock_file):
        """Test main function with default file path."""
        with patch('builtins.print') as mock_print:
            main()
            mock_file.assert_called_once_with("./data/data.txt", "r")
            mock_print.assert_called_once()

    @patch('traffic_analyzer.open', new_callable=mock_open, read_data="2021-12-01T05:00:00 5\n2021-12-01T05:30:00 12\n2021-12-01T06:00:00 14\n")
    @patch('sys.argv', ['main.py', '--inputfile', 'custom_data.txt'])
    def test_main_custom_file(self, mock_file):
        """Test main function with custom file path."""
        with patch('builtins.print') as mock_print:
            main()
            mock_file.assert_called_once_with("custom_data.txt", "r")
            mock_print.assert_called_once()

    @patch('main.TrafficAnalyzer')
    @patch('main.TrafficAnalysisResult')
    @patch('sys.argv', ['main.py'])
    def test_main_creates_traffic_analyzer_with_default_path(self, mock_result_class, mock_analyzer_class):
        """Test that main creates TrafficAnalyzer with default file path."""
        mock_analyzer_instance = MagicMock()
        mock_analyzer_class.return_value = mock_analyzer_instance
        mock_result_instance = MagicMock()
        mock_result_class.return_value = mock_result_instance

        with patch('builtins.print'):
            main()

        mock_analyzer_class.assert_called_once_with("./data/data.txt")

    @patch('main.TrafficAnalyzer')
    @patch('main.TrafficAnalysisResult')
    @patch('sys.argv', ['main.py', '--inputfile', '/path/to/custom/file.txt'])
    def test_main_creates_traffic_analyzer_with_custom_path(self, mock_result_class, mock_analyzer_class):
        """Test that main creates TrafficAnalyzer with custom file path."""
        mock_analyzer_instance = MagicMock()
        mock_analyzer_class.return_value = mock_analyzer_instance
        mock_result_instance = MagicMock()
        mock_result_class.return_value = mock_result_instance

        with patch('builtins.print'):
            main()

        mock_analyzer_class.assert_called_once_with("/path/to/custom/file.txt")

    @patch('main.TrafficAnalyzer')
    @patch('main.TrafficAnalysisResult')
    @patch('sys.argv', ['main.py'])
    def test_main_calls_all_analyzer_methods(self, mock_result_class, mock_analyzer_class):
        """Test that main calls all required methods on TrafficAnalyzer."""
        mock_analyzer_instance = MagicMock()
        mock_analyzer_class.return_value = mock_analyzer_instance
        mock_result_instance = MagicMock()
        mock_result_class.return_value = mock_result_instance

        with patch('builtins.print'):
            main()

        # Verify all analyzer methods are called
        mock_analyzer_instance.calculate_traffic.assert_called_once()
        mock_analyzer_instance.get_daily_traffic.assert_called_once()
        mock_analyzer_instance.get_top_n_half_hours.assert_called_once_with(n=3)
        mock_analyzer_instance.least_cars_in_ninety_mins.assert_called_once()

    @patch('main.TrafficAnalyzer')
    @patch('main.TrafficAnalysisResult')
    @patch('sys.argv', ['main.py'])
    def test_main_creates_traffic_analysis_result_with_correct_data(self, mock_result_class, mock_analyzer_class):
        """Test that main creates TrafficAnalysisResult with correct data from analyzer."""
        mock_analyzer_instance = MagicMock()
        mock_analyzer_class.return_value = mock_analyzer_instance
        mock_result_instance = MagicMock()
        mock_result_class.return_value = mock_result_instance

        # Set up mock return values
        total_traffic = 117
        daily_traffic = {"2021-12-01": 117}
        top_half_hours = [
            TrafficRecord(timestamp="2021-12-01T07:30:00", car_count=46),
            TrafficRecord(timestamp="2021-12-01T07:00:00", car_count=25),
            TrafficRecord(timestamp="2021-12-01T06:30:00", car_count=15)
        ]
        least_ninety_mins = TrafficRecord(
            timestamp="2021-12-01T05:00:00", car_count=31, duration_mins=90
        )

        mock_analyzer_instance.calculate_traffic.return_value = total_traffic
        mock_analyzer_instance.get_daily_traffic.return_value = daily_traffic
        mock_analyzer_instance.get_top_n_half_hours.return_value = top_half_hours
        mock_analyzer_instance.least_cars_in_ninety_mins.return_value = least_ninety_mins

        with patch('builtins.print'):
            main()

        # Verify TrafficAnalysisResult is created with correct arguments
        mock_result_class.assert_called_once_with(
            total_traffic=total_traffic,
            daily_traffic=daily_traffic,
            top_n_half_hours=top_half_hours,
            least_ninety_mins_traffic=least_ninety_mins
        )

    @patch('main.TrafficAnalyzer')
    @patch('main.TrafficAnalysisResult')
    @patch('sys.argv', ['main.py'])
    def test_main_prints_analysis_result(self, mock_result_class, mock_analyzer_class):
        """Test that main prints the TrafficAnalysisResult."""
        mock_analyzer_instance = MagicMock()
        mock_analyzer_class.return_value = mock_analyzer_instance
        mock_result_instance = MagicMock()
        mock_result_instance.__str__ = MagicMock(return_value="Test output string")
        mock_result_class.return_value = mock_result_instance

        with patch('builtins.print') as mock_print:
            main()

        # Verify print is called with the result instance
        mock_print.assert_called_once_with(mock_result_instance)

    @patch('sys.argv', ['main.py', '--inputfile', 'nonexistent_file.txt'])
    def test_main_with_nonexistent_file(self):
        """Test main function behavior with nonexistent file."""
        with self.assertRaises(FileNotFoundError):
            main()

    @patch('main.TrafficAnalyzer')
    @patch('sys.argv', ['main.py'])
    def test_main_handles_analyzer_errors(self, mock_analyzer_class):
        """Test that main handles errors from TrafficAnalyzer gracefully."""
        # Make TrafficAnalyzer raise an exception
        mock_analyzer_class.side_effect = ValueError("Invalid data format")
        
        with self.assertRaises(ValueError) as context:
            main()
        
        self.assertEqual(str(context.exception), "Invalid data format")

    def test_main_flow_integration(self):
        """Test the complete flow of main function with minimal mocking."""
        test_data = """2021-12-01T05:00:00 5
2021-12-01T05:30:00 12
2021-12-01T06:00:00 14
2021-12-01T06:30:00 15"""

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(test_data)
            temp_file_path = temp_file.name

        try:
            with patch('sys.argv', ['main.py', '--inputfile', temp_file_path]):
                # Capture the output
                with patch('builtins.print') as mock_print:
                    main()
                    
                    # Verify print was called
                    self.assertTrue(mock_print.called)
                    
                    # Get the printed result
                    result = mock_print.call_args[0][0]
                    
                    # Verify it's the correct type
                    self.assertIsInstance(result, TrafficAnalysisResult)
                    
                    # Verify the data is processed correctly
                    self.assertEqual(result.total_traffic, 46)  # 5+12+14+15
                    self.assertIn("2021-12-01", result.daily_traffic)
                    self.assertEqual(len(result.top_n_half_hours), 3)  # Should have 3 records (n=3)
                    
        finally:
            os.unlink(temp_file_path)


if __name__ == '__main__':
    unittest.main()
