from dataclasses import dataclass

@dataclass
class TrafficRecord:
    """
    Class to hold individual traffic record.
    """
    timestamp: str
    car_count: int
    duration_mins: int = 30

@dataclass(repr=False)
class TrafficAnalysisResult:
    """
    Class to hold the results of traffic analysis.
    """
    total_traffic: int
    daily_traffic: dict
    top_n_half_hours: list
    least_ninety_mins_traffic: TrafficRecord

    def __repr__(self):
        """
        Custom string representation for better readability.
        """
        result = []
        result.append(f"The number of cars seen in total: {self.total_traffic}")

        result.append(f"\n\nDaily traffic...")
        result.append("Date       Number of cars seen")
        result.append("-------------------------------")
        for date, traffic in self.daily_traffic.items():
            result.append(f"{date}\t{traffic}")

        result.append(f"\n\nTop 3 half hours with highest traffic...")
        result.append("Timestamp           Number of cars seen")
        result.append("---------------------------------------")
        for record in self.top_n_half_hours:
            result.append(f"{record.timestamp} {record.car_count}")

        result.append(f"Timestamp with least number of cars seen in next 90 minutes: {self.least_ninety_mins_traffic.timestamp}")
        
        return "\n".join(result)
