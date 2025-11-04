import argparse
import pprint
from datetime import datetime, timedelta

def main():
    """
    Main function of the program.
    if --inputfile is provided then the file will be read from the given path,
    else it will read from the default path ./data.txt
    1. Transforms the data into a dictionary
    2. Calculates total traffic
    3. Calculates daily traffic
    4. Finds top 3 half hours with highest traffic
    5. Finds contiguous 90 minutes intervals car counts
    6. Prints the results to the console
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputfile", help="Filepath of machine generated traffic data")
    args = parser.parse_args()
    
    if (not args.inputfile):
        file_path = "./data.txt"
    else: 
        file_path = args.inputfile

    with open(file_path, "r") as data_file:
        data_dict = transform_data(data_file)

    pprint.pp(data_dict)

    print("\n\nCalculating total traffic...")
    total_traffic = calculate_traffic(data_dict)
    print(f"The number of cars seen in total: {total_traffic}")

    print("\n\nCalculating daily traffic...")
    print("Date       Number of cars seen")
    print("-------------------------------")
    daily_traffic = get_daily_traffic(data_dict)
    for date, traffic in daily_traffic.items():
        print(f"{date}\t{traffic}")

    print("\n\nFinding top 3 half hours with highest traffic...")
    print("Timestamp           Number of cars seen")
    print("---------------------------------------")
    for timestamp, traffic in get_top_n_half_hours(data_dict, n=3):
        print(f"{timestamp} {traffic}")

    print("\n\nFinding contiguous 90 minutes intervals car counts...")
    contiguous_ninty_mins_traffic = get_contiguous_ninty_mins_traffic(data_dict)
    least_cars_timestamp = min(contiguous_ninty_mins_traffic.items(), key=lambda x: x[1])
    print("Timestamp           Number of cars seen in next 90 minutes")
    print("---------------------------------------------------")
    print(f"{least_cars_timestamp[0]}\t{least_cars_timestamp[1]}")

def transform_data(data_file):
    """
    Function to transform the data from file into a dictionary.
    """
    data = [(x.strip().split()) for x in data_file.readlines()]
    data_dict = {k: int(v) for k, v in data}
    return data_dict

def calculate_traffic(data_dict):
    """
    Function to calculate total traffic from the data dictionary.
    """
    return sum(data_dict.values())

def get_date(timestamp):
    """
    Function to convert timestamp to date in YYYY-MM-DD format.
    """
    return datetime.fromisoformat(timestamp).date().strftime("%Y-%m-%d")

def get_daily_traffic(data_dict):
    """
    Function to calculate daily traffic from the data dictionary.
    """

    date_set = {get_date(timestamp) for timestamp in data_dict.keys()}

    return {
        dd: sum(v for k, v in data_dict.items() if get_date(k) == dd)
        for dd in sorted(date_set)
    }

def get_top_n_half_hours(data_dict, n=3):
    """
    Function to get top n half hours with highest traffic.
    """
    return sorted(data_dict.items(), key=lambda x: x[1], reverse=True)[0:n]

def next_ts(timestamp, delta_mins):
    """
    Function to get the next timestamp after adding delta minutes.
    """
    timestamp_dt = datetime.fromisoformat(timestamp)
    new_timestamp_dt = timestamp_dt + timedelta(minutes=delta_mins)
    return new_timestamp_dt.isoformat()

def has_contiguous_records(timestamp: str, data_dict: dict) -> bool:
    """
    Function to check if the given timestamp has contiguous records
    for the next 30 minutes and 60 minutes.
    """
    return next_ts(timestamp, 30) in data_dict.keys() and next_ts(timestamp, 60) in data_dict.keys()

def get_contiguous_ninty_mins_traffic(data_dict):
    """
    Function to calculate car count for contiguous 90 minutes intervals.
    """
    return {
        timestamp: sum(data_dict[t] for t in [timestamp, next_ts(timestamp, 30), next_ts(timestamp, 60)])
        for timestamp in data_dict if has_contiguous_records(timestamp, data_dict)
    }

if __name__ == "__main__":
    main()