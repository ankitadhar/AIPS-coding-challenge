from dataclasses import dataclass, field
from datetime import datetime, timedelta
from model import TrafficRecord

@dataclass
class TrafficAnalyzer:
    data_file_path: str
    traffic_data: list[TrafficRecord] = field(default_factory=list)

    def __post_init__(self):
        self._transform_data()

    def calculate_traffic(self):
        """
        Function to calculate total traffic from the data dictionary.
        """
        return sum(record.car_count for record in self.traffic_data)

    def get_daily_traffic(self):
        """
        Function to calculate daily traffic from the data dictionary.
        """

        date_set = {self._get_date(record.timestamp) for record in self.traffic_data}

        return {
            dd: sum(record.car_count for record in self.traffic_data if self._get_date(record.timestamp) == dd)
            for dd in sorted(date_set)
        }

    def get_top_n_half_hours(self, n=3):
        """
        Function to get top n half hours with highest traffic.
        """
        return sorted(self.traffic_data, key=lambda x: x.car_count, reverse=True)[0:n]
    
    def least_cars_in_ninety_mins(self):
        """
        Function to find the timestamp with least number of cars seen in next 90 minutes.
        """
        least_traffic_ninty_mins = min(self._get_contiguous_ninety_mins_traffic(), key=lambda x: x.car_count)
        return least_traffic_ninty_mins

    def _transform_data(self):
        """
        Function to transform the data from file into a dictionary.
        """
        with open(self.data_file_path, "r") as data_file:
            data = [(x.strip().split()) for x in data_file.readlines()]
            self.traffic_data = [TrafficRecord(timestamp=k, car_count=int(v)) for k, v in data]

    def _get_date(self, timestamp):
        """
        Function to convert timestamp to date in YYYY-MM-DD format.
        """
        return datetime.fromisoformat(timestamp).date().strftime("%Y-%m-%d")

    def _next_ts(self, timestamp, delta_mins):
        """
        Function to get the next timestamp after adding delta minutes.
        """
        timestamp_dt = datetime.fromisoformat(timestamp)
        new_timestamp_dt = timestamp_dt + timedelta(minutes=delta_mins)
        return new_timestamp_dt.isoformat()

    def _has_contiguous_records(self, i: int) -> bool:
        """
        Function to check if the given timestamp has contiguous records
        for the next 30 minutes and 60 minutes.
        """
        timestamp = self.traffic_data[i].timestamp
        if i + 2 < len(self.traffic_data):
            return (self.traffic_data[i + 1].timestamp == self._next_ts(timestamp, 30) and
                    self.traffic_data[i + 2].timestamp == self._next_ts(timestamp, 60))
        return False

    def _get_next_records(self, i: int):
        """
        Function to get the next records for the given timestamp.
        """
        return [
            self.traffic_data[j]
            for j in range(i, i + 3)
        ]

    def _get_contiguous_ninety_mins_traffic(self):
        """
        Function to calculate car count for contiguous 90 minutes intervals.
        """
        return [
            TrafficRecord(
                timestamp=self.traffic_data[i].timestamp,
                car_count=sum(record.car_count for record in self._get_next_records(i)),
                duration_mins=90
            )
            for i in range(len(self.traffic_data)) if self._has_contiguous_records(i)
        ]
